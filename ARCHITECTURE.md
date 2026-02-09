# SQL Agent - Architecture Document

**Project Name:** SQL Agent - Intelligent Database & Document Assistant

<!-- **Version:** 1.0 (Proposed)
**Date:** February 6, 2026
**Status:** Awaiting Architectural Review -->

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State (Phase 0)](#2-current-state-phase-0)
3. [Proposed Architecture Overview](#3-proposed-architecture-overview)
4. [System Architecture Diagram](#4-system-architecture-diagram)
5. [Backend Architecture](#5-backend-architecture)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Complete Folder Structure](#7-complete-folder-structure)
8. [Data Models](#8-data-models)
9. [API Contract](#9-api-contract)
10. [Document Ingestion Pipeline (RAG)](#10-document-ingestion-pipeline-rag)
11. [Thread Memory & Conversation Management](#11-thread-memory--conversation-management)
12. [UI/UX Design](#12-uiux-design)
13. [Technology Stack](#13-technology-stack)
14. [Storage Strategy](#14-storage-strategy)
15. [Security Considerations](#15-security-considerations)
<!-- 16. [Phased Rollout Plan](#16-phased-rollout-plan)
16. [Risks & Mitigations](#17-risks--mitigations) -->

---

## 1. Executive Summary

SQL Agent is an AI-powered application that allows users to query SQL databases using natural language. The system translates user questions into SQL queries, executes them, and returns human-readable answers.

**Current state:** CLI-only tool using LangChain + Google Gemini, querying a SQLite database.

**Proposed evolution:** A full-stack web application with:

- **Chat-based UI** (Next.js) with thread memory and conversation history
- **Document management** (upload, index, delete) for RAG capabilities
- **Hybrid agent** that can answer from both structured data (SQL) and unstructured documents (RAG)
- **Streaming responses** for real-time UX
- **Scalable backend** (FastAPI) with clear API contracts

---

## 2. Current State (Phase 0)

### Existing Codebase

```
SQL_agent/
├── main.py                         # Entry point
├── .env                            # Environment variables (API keys)
├── Chinook.db                      # SQLite sample database
└── src/
    └── sql_agent/
        ├── __init__.py             # Package init
        ├── agent.py                # Agent creation + execution logic
        ├── app.py                  # Application builder (wires dependencies)
        ├── cli.py                  # CLI loop (read-eval-print)
        ├── db.py                   # Database connection + download
        ├── input_handler.py        # User input iterator
        ├── prompts.py              # System prompt builder
        └── settings.py             # Configuration dataclass
```

### Current Flow

```
User (CLI) → input_handler.py → cli.py → agent.py → LangChain SQL Toolkit → SQLite DB
                                                          ↓
                                              Gemini 2.5 Flash (LLM)
                                                          ↓
                                              Answer printed to console
```

### Current Technology

| Component   | Technology                     |
| ----------- | ------------------------------ |
| Language    | Python 3.13                    |
| LLM         | Google Gemini 2.5 Flash        |
| Framework   | LangChain + LangGraph          |
| SQL Toolkit | LangChain `SQLDatabaseToolkit` |
| Database    | SQLite (Chinook sample DB)     |
| Interface   | CLI (stdin/stdout)             |

### Key Existing Modules

- **`settings.py`** - Immutable `Settings` dataclass with model name, DB URL, DB path, and `top_k` limit.
- **`db.py`** - Downloads database file if not present locally; creates LangChain `SQLDatabase` instance.
- **`prompts.py`** - Builds a dynamic system prompt instructing the agent on SQL query behavior, safety (no DML), and best practices.
- **`agent.py`** - Creates the LangChain agent with SQL tools; runs the agent with streaming; extracts text from various response formats.
- **`app.py`** - Orchestrator that loads environment, initializes settings, database, model, and returns a ready-to-use agent.
- **`cli.py`** - REPL loop that takes user questions and prints agent answers.

---

## 3. Proposed Architecture Overview

### Design Principles

1. **Separation of Concerns** - Frontend, backend API, agent logic, and storage are distinct layers.
2. **Streaming-First** - All agent responses use Server-Sent Events (SSE) for real-time display.
3. **Modular Agents** - SQL agent, RAG agent, and hybrid agent are independent modules behind a unified API.
4. **Thread Isolation** - Each conversation has its own memory context and optionally attached documents.
5. **Progressive Enhancement** - The system is built in phases; each phase is independently deployable and valuable.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                            │
│                                                                       │
│  ┌────────────┐   ┌──────────────────┐   ┌────────────────────────┐  │
│  │  Sidebar    │   │   Chat Interface  │   │  Document Manager      │  │
│  │  - Threads  │   │   - Messages      │   │  - Upload/Delete       │  │
│  │  - Documents│   │   - Streaming     │   │  - Processing Status   │  │
│  │  - Search   │   │   - In-chat upload│   │  - Preview             │  │
│  └─────┬──────┘   └────────┬─────────┘   └───────────┬────────────┘  │
│        └──────────────────┬┘                          │               │
│                    Next.js Route Handlers              │               │
│                    (API Proxy Layer)                    │               │
└───────────────────────────┬───────────────────────────┘               │
                            │  HTTP / SSE                                │
┌───────────────────────────┴──────────────────────────────────────────┐
│                         BACKEND (FastAPI)                              │
│                                                                       │
│  ┌────────────┐   ┌──────────────────┐   ┌────────────────────────┐  │
│  │ Chat API    │   │  Thread API       │   │  Document API          │  │
│  │ /chat/stream│   │  CRUD /threads    │   │  CRUD /documents       │  │
│  └──────┬─────┘   └────────┬─────────┘   └───────────┬────────────┘  │
│         │                  │                          │               │
│  ┌──────▼──────────────────▼──────────────────────────▼────────────┐  │
│  │                      Agent Router                                │  │
│  │              (selects SQL / RAG / Hybrid agent)                   │  │
│  └──────┬─────────────────┬────────────────────────┬───────────────┘  │
│         │                 │                        │                  │
│  ┌──────▼─────┐   ┌──────▼────────┐   ┌──────────▼──────────────┐   │
│  │ SQL Agent   │   │  RAG Agent     │   │  Hybrid Agent           │   │
│  │ (existing)  │   │  (Phase 2)     │   │  SQL + RAG (Phase 2)    │   │
│  └──────┬─────┘   └──────┬────────┘   └──────────┬──────────────┘   │
│         │                 │                        │                  │
│  ┌──────▼─────┐   ┌──────▼────────┐   ┌──────────▼──────────────┐   │
│  │  SQLite /   │   │  ChromaDB      │   │  Thread Memory          │   │
│  │  PostgreSQL │   │  (Vector Store)│   │  (LangGraph SqliteSaver)│   │
│  └────────────┘   └───────────────┘   └─────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 4. System Architecture Diagram

### Request Flow: User Asks a Question

```
  ┌─────────┐        ┌──────────────┐        ┌──────────────┐
  │  Browser │───────>│  Next.js      │───────>│  FastAPI      │
  │  (React) │  SSE   │  Route Handler│  HTTP   │  /chat/stream │
  │          │<───────│  /api/chat    │<───────│               │
  └─────────┘        └──────────────┘        └──────┬───────┘
                                                     │
                                              ┌──────▼───────┐
                                              │ Agent Router  │
                                              │ (mode check)  │
                                              └──────┬───────┘
                                                     │
                          ┌──────────────────────────┼──────────────────┐
                          │                          │                  │
                   ┌──────▼─────┐           ┌───────▼──────┐   ┌──────▼──────┐
                   │ SQL Agent   │           │  RAG Agent    │   │ Hybrid Agent│
                   │             │           │               │   │             │
                   │ 1. List     │           │ 1. Embed      │   │ 1. Retrieve │
                   │    tables   │           │    query      │   │    docs     │
                   │ 2. Get      │           │ 2. Search     │   │ 2. Query    │
                   │    schema   │           │    vectors    │   │    SQL DB   │
                   │ 3. Write    │           │ 3. Build      │   │ 3. Combine  │
                   │    SQL      │           │    context    │   │    context  │
                   │ 4. Execute  │           │ 4. Generate   │   │ 4. Generate │
                   │ 5. Respond  │           │    answer     │   │    answer   │
                   └──────┬─────┘           └───────┬──────┘   └──────┬──────┘
                          │                         │                  │
                   ┌──────▼─────┐           ┌───────▼──────┐          │
                   │  SQLite DB  │           │  ChromaDB     │          │
                   └────────────┘           └──────────────┘          │
                                                                      │
                                                               ┌──────▼──────┐
                                                               │ Both DBs    │
                                                               └─────────────┘
```

### Request Flow: Document Upload

```
  ┌─────────┐        ┌──────────────┐        ┌──────────────────────────┐
  │  Browser │───────>│  Next.js      │───────>│  FastAPI                  │
  │  (file)  │ POST   │  /api/documents│ POST  │  /documents               │
  └─────────┘        └──────────────┘        └──────────┬───────────────┘
                                                        │
                                                 ┌──────▼───────────────┐
                                                 │ Document Ingestion    │
                                                 │ Pipeline              │
                                                 │                       │
                                                 │ 1. Save raw file      │
                                                 │ 2. Load document      │
                                                 │    (LangChain Loader) │
                                                 │ 3. Split into chunks  │
                                                 │ 4. Generate embeddings│
                                                 │ 5. Store in ChromaDB  │
                                                 │ 6. Update metadata DB │
                                                 └──────────────────────┘
```

---

## 5. Backend Architecture

### 5.1 Module Responsibilities

| Module                    | Responsibility                                                      |
| ------------------------- | ------------------------------------------------------------------- |
| `api/main.py`             | FastAPI app initialization, CORS, lifespan events                   |
| `api/routes/chat.py`      | Chat streaming endpoint                                             |
| `api/routes/threads.py`   | CRUD operations for conversation threads                            |
| `api/routes/documents.py` | Document upload, list, delete endpoints                             |
| `api/routes/database.py`  | Database schema and table preview endpoints                         |
| `core/agent.py`           | Agent creation (SQL, RAG, Hybrid) - evolved from current `agent.py` |
| `core/prompts.py`         | System prompt templates - evolved from current `prompts.py`         |
| `core/app.py`             | Application builder / dependency wiring                             |
| `core/settings.py`        | Configuration - evolved from current `settings.py`                  |
| `services/db.py`          | SQL database connection management                                  |
| `services/vectorstore.py` | ChromaDB connection and operations                                  |
| `services/ingestion.py`   | Document loading, splitting, embedding pipeline                     |
| `services/memory.py`      | Thread memory management (LangGraph checkpointer)                   |
| `models/schemas.py`       | Pydantic request/response models                                    |
| `models/database.py`      | SQLAlchemy ORM models (Thread, Message, Document)                   |

### 5.2 Agent Router Logic

```python
# Pseudocode for agent selection
def get_agent(mode: str, thread_id: str):
    match mode:
        case "sql":
            return sql_agent           # Current implementation
        case "rag":
            return rag_agent           # Phase 2
        case "hybrid":
            return hybrid_agent        # Phase 2 (SQL tools + retriever tool)
```

### 5.3 Streaming Response Format (SSE)

Each SSE event follows this structure:

```
event: step
data: {"type": "thinking", "content": "Looking at database tables..."}

event: step
data: {"type": "sql_query", "content": "SELECT g.Name, COUNT(*) ..."}

event: step
data: {"type": "sql_result", "content": [{"Genre": "Rock", "Count": 131}]}

event: step
data: {"type": "source", "content": {"doc_id": "abc", "page": 3, "snippet": "..."}}

event: answer
data: {"type": "final", "content": "The most popular genre is Rock with 131 tracks."}
```

---

## 6. Frontend Architecture

### 6.1 UI Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  HEADER                                              [Settings] [?] │
├──────────────────┬───────────────────────────────────────────────────┤
│                  │                                                    │
│     SIDEBAR      │                MAIN CONTENT                       │
│   (resizable)    │                                                    │
│                  │  ┌────────────────────────────────────────────┐   │
│  ┌────────────┐  │  │  Thread Header                             │   │
│  │ + New Chat  │  │  │  Title: "Sales Analysis"  [3 docs] [SQL]  │   │
│  └────────────┘  │  └────────────────────────────────────────────┘   │
│                  │                                                    │
│  ── Chats ─────  │  ┌────────────────────────────────────────────┐   │
│  │ Sales Anal. │  │  │                                            │   │
│  │ User Report │  │  │  User: How many albums per genre?          │   │
│  │ Revenue Q4  │  │  │                                            │   │
│  │             │  │  │  Agent: [Thinking...] [SQL Query]          │   │
│  │             │  │  │         ┌──────────────────────┐           │   │
│  ── Documents ─  │  │         │  Genre   │  Count     │           │   │
│  │ report.pdf  │  │  │         │  Rock    │  131       │           │   │
│  │ schema.txt  │  │  │         │  Latin   │  28        │           │   │
│  │ notes.docx  │  │  │         └──────────────────────┘           │   │
│  │             │  │  │                                            │   │
│  │ [+ Upload]  │  │  │  The most popular genre is Rock...         │   │
│  │ [🗑 Manage] │  │  │                                            │   │
│  └────────────┘  │  └────────────────────────────────────────────┘   │
│                  │                                                    │
│                  │  ┌────────────────────────────────────────────┐   │
│                  │  │ [📎] Ask about your database...      [Send] │   │
│                  │  │ [SQL ▾]  attached: quarterly.pdf  [x]       │   │
│                  │  └────────────────────────────────────────────┘   │
├──────────────────┴───────────────────────────────────────────────────┤
│  Connected: Chinook.db  │  Model: gemini-2.5-flash  │  Threads: 3   │
└──────────────────────────────────────────────────────────────────────┘
```

### 6.2 Component Hierarchy

```
RootLayout
├── Sidebar
│   ├── NewChatButton
│   ├── ThreadSection
│   │   ├── ThreadSearchBar
│   │   └── ThreadList
│   │       └── ThreadItem (repeating)
│   │           ├── ThreadTitle
│   │           ├── ThreadPreview
│   │           └── ThreadContextMenu (rename, delete, pin)
│   ├── DocumentSection
│   │   ├── DocumentUploadButton
│   │   └── DocumentList
│   │       └── DocumentItem (repeating)
│   │           ├── FileIcon
│   │           ├── FileName
│   │           ├── ProcessingStatus
│   │           └── DocumentActions (preview, delete)
│   └── SidebarFooter (storage usage)
│
├── MainContent
│   ├── ThreadHeader
│   │   ├── EditableTitle
│   │   ├── AttachedDocsBadge
│   │   ├── ModeIndicator
│   │   └── ThreadActions (clear, export)
│   │
│   ├── MessageList (virtualized scroll)
│   │   ├── UserMessage
│   │   │   ├── MessageContent
│   │   │   └── AttachedFileChips
│   │   └── AgentMessage
│   │       ├── ThinkingAccordion
│   │       ├── SQLCodeBlock (syntax highlighted)
│   │       ├── SQLResultTable (sortable)
│   │       ├── MarkdownContent
│   │       └── SourceCitations
│   │           └── SourceCard (repeating)
│   │
│   └── ChatInput
│       ├── FileAttachButton
│       ├── AttachedFileStrip
│       ├── TextInput (auto-resize)
│       ├── ModeSelector (SQL / RAG / Hybrid)
│       └── SendButton
│
└── StatusBar
    ├── ConnectionStatus
    ├── ModelInfo
    └── ThreadCount
```

### 6.3 Key Frontend Features

| Feature                 | Description                                                      |
| ----------------------- | ---------------------------------------------------------------- |
| **Streaming Display**   | Token-by-token rendering using Vercel AI SDK `useChat` hook      |
| **Thread Persistence**  | Conversations saved and restored from backend                    |
| **In-Chat Upload**      | Attach files via 📎 button; files processed and added to context |
| **SQL Result Tables**   | Sortable, expandable tables rendered from query results          |
| **Syntax Highlighting** | SQL queries displayed with syntax colors and copy button         |
| **Markdown Rendering**  | Agent responses rendered as rich markdown                        |
| **Source Citations**    | RAG answers show which documents were referenced                 |
| **Thinking Steps**      | Collapsible accordion showing agent's intermediate reasoning     |
| **Responsive Sidebar**  | Collapsible sidebar with resizable width                         |
| **Dark/Light Mode**     | Theme toggle via shadcn/ui theme provider                        |

---

## 7. Complete Folder Structure

### 7.1 Root Structure

```
SQL_agent/
├── backend/                          # Python backend (FastAPI + Agents)
├── frontend/                         # Next.js frontend application
├── docker-compose.yml                # Multi-service orchestration
├── .gitignore                        # Git ignore rules
├── ARCHITECTURE.md                   # This document
└── README.md                         # Project overview and setup guide
```

### 7.2 Backend Structure

```
backend/
├── main.py                           # FastAPI app entry point (uvicorn)
├── requirements.txt                  # Python dependencies with versions
├── .env                              # Environment variables (gitignored)
├── .env.example                      # Template for environment variables
├── Chinook.db                        # SQLite sample database (gitignored)
├── threads.db                        # Thread memory persistence (gitignored)
│
├── api/                              # --- API Layer ---
│   ├── __init__.py
│   ├── main.py                       # FastAPI app factory, CORS, lifespan
│   ├── dependencies.py               # Dependency injection (agent, db, etc.)
│   └── routes/
│       ├── __init__.py
│       ├── chat.py                   # POST /chat/stream (SSE streaming)
│       ├── threads.py                # CRUD /threads, /threads/{id}
│       ├── documents.py              # CRUD /documents, upload endpoint
│       └── database.py               # GET /database/schema, /tables/{name}
│
├── core/                             # --- Core Agent Logic ---
│   ├── __init__.py
│   ├── agent.py                      # Agent creation (SQL, RAG, Hybrid)
│   ├── agent_router.py               # Routes to correct agent by mode
│   ├── prompts.py                    # System prompt templates
│   ├── app.py                        # Application builder / wiring
│   └── settings.py                   # Settings dataclass + env loading
│
├── services/                         # --- Business Logic & Integrations ---
│   ├── __init__.py
│   ├── db.py                         # SQL database connection management
│   ├── vectorstore.py                # ChromaDB connection and operations
│   ├── ingestion.py                  # Document loading, splitting, embedding
│   ├── memory.py                     # LangGraph thread memory (SqliteSaver)
│   └── storage.py                    # File storage (local / S3 abstraction)
│
├── models/                           # --- Data Models ---
│   ├── __init__.py
│   ├── schemas.py                    # Pydantic request/response models
│   └── database.py                   # SQLAlchemy ORM (Thread, Message, Doc)
│
├── uploads/                          # Uploaded document files (gitignored)
│
└── tests/                            # --- Test Suite ---
    ├── __init__.py
    ├── conftest.py                   # Shared fixtures
    ├── test_agent.py                 # Agent unit tests
    ├── test_routes.py                # API endpoint tests
    ├── test_ingestion.py             # Document pipeline tests
    └── test_memory.py                # Thread memory tests
```

### 7.3 Frontend Structure

```
frontend/
├── package.json                      # Dependencies and scripts
├── package-lock.json                 # Lock file
├── next.config.ts                    # Next.js configuration
├── tsconfig.json                     # TypeScript configuration
├── tailwind.config.ts                # Tailwind CSS configuration
├── postcss.config.js                 # PostCSS configuration
├── .env.local                        # Frontend env vars (gitignored)
├── .env.example                      # Template for frontend env vars
│
├── public/                           # Static assets
│   ├── favicon.ico
│   └── logo.svg
│
├── app/                              # --- Next.js App Router ---
│   ├── layout.tsx                    # Root layout (sidebar + main)
│   ├── page.tsx                      # Home → redirect to /chat/new
│   ├── globals.css                   # Global styles + Tailwind imports
│   ├── providers.tsx                 # Theme, Zustand, QueryClient providers
│   │
│   ├── chat/
│   │   └── [threadId]/
│   │       ├── page.tsx              # Chat thread view
│   │       └── loading.tsx           # Loading skeleton
│   │
│   └── api/                          # --- Next.js Route Handlers ---
│       ├── chat/
│       │   └── route.ts             # POST - proxy to FastAPI /chat/stream
│       ├── threads/
│       │   ├── route.ts             # GET (list), POST (create)
│       │   └── [id]/
│       │       └── route.ts         # GET, PATCH, DELETE
│       └── documents/
│           ├── route.ts             # GET (list), POST (upload)
│           └── [id]/
│               └── route.ts         # GET, DELETE
│
├── components/                       # --- React Components ---
│   │
│   ├── layout/                       # Layout components
│   │   ├── Sidebar.tsx               # Main sidebar container
│   │   ├── SidebarToggle.tsx         # Collapse/expand button
│   │   ├── Header.tsx                # Top header bar
│   │   └── StatusBar.tsx             # Bottom status bar
│   │
│   ├── threads/                      # Thread-related components
│   │   ├── ThreadList.tsx            # Scrollable thread list
│   │   ├── ThreadItem.tsx            # Single thread row
│   │   ├── ThreadSearchBar.tsx       # Search within threads
│   │   ├── ThreadHeader.tsx          # Thread title + actions
│   │   └── NewChatButton.tsx         # Create new thread button
│   │
│   ├── documents/                    # Document-related components
│   │   ├── DocumentSection.tsx       # Sidebar docs section
│   │   ├── DocumentItem.tsx          # Single document row
│   │   ├── DocumentUploadButton.tsx  # Upload trigger button
│   │   ├── DocumentUploadDialog.tsx  # Upload modal with dropzone
│   │   ├── DocumentPreview.tsx       # Document content preview
│   │   └── ProcessingBadge.tsx       # Indexing status indicator
│   │
│   ├── chat/                         # Chat interface components
│   │   ├── MessageList.tsx           # Virtualized message list
│   │   ├── UserMessage.tsx           # User message bubble
│   │   ├── AgentMessage.tsx          # Agent message bubble
│   │   ├── ChatInput.tsx             # Input bar container
│   │   ├── FileAttachButton.tsx      # 📎 attach button
│   │   ├── AttachedFileStrip.tsx     # Inline file chips
│   │   ├── AttachedFileChip.tsx      # Single file chip (removable)
│   │   ├── ModeSelector.tsx          # SQL / RAG / Hybrid toggle
│   │   ├── SendButton.tsx            # Submit button
│   │   ├── MarkdownRenderer.tsx      # Markdown display
│   │   ├── SQLCodeBlock.tsx          # SQL syntax highlight + copy
│   │   ├── SQLResultTable.tsx        # Sortable result table
│   │   ├── SourceCitation.tsx        # RAG source reference card
│   │   ├── ThinkingAccordion.tsx     # Agent reasoning steps
│   │   └── StreamingIndicator.tsx    # Typing / loading animation
│   │
│   └── ui/                           # shadcn/ui primitives
│       ├── button.tsx
│       ├── input.tsx
│       ├── dialog.tsx
│       ├── dropdown-menu.tsx
│       ├── scroll-area.tsx
│       ├── accordion.tsx
│       ├── badge.tsx
│       ├── card.tsx
│       ├── separator.tsx
│       ├── skeleton.tsx
│       ├── table.tsx
│       ├── textarea.tsx
│       ├── tooltip.tsx
│       └── theme-toggle.tsx
│
├── lib/                              # --- Utilities & Configuration ---
│   ├── api-client.ts                 # Typed HTTP client for backend
│   ├── types.ts                      # TypeScript type definitions
│   ├── constants.ts                  # App-wide constants
│   ├── utils.ts                      # Helper functions
│   └── stores/                       # Zustand state management
│       ├── thread-store.ts           # Thread list + active thread state
│       ├── document-store.ts         # Document list + upload state
│       └── ui-store.ts              # Sidebar open/closed, theme, etc.
│
└── hooks/                            # --- Custom React Hooks ---
    ├── use-chat-stream.ts            # SSE streaming chat hook
    ├── use-threads.ts                # Thread CRUD operations
    ├── use-documents.ts              # Document CRUD + upload
    └── use-sidebar.ts                # Sidebar state management
```

### 7.4 Docker & DevOps Structure

```
SQL_agent/
├── docker-compose.yml                # Orchestrate frontend + backend
├── backend/
│   └── Dockerfile                    # Python backend container
└── frontend/
    └── Dockerfile                    # Next.js frontend container
```

---

## 8. Data Models

### 8.1 Thread (Conversation)

```python
class Thread:
    id: str                    # UUID v4
    title: str                 # Auto-generated from first message, editable
    mode: str                  # "sql" | "rag" | "hybrid"
    attached_doc_ids: list[str]# Documents pinned to this thread's context
    is_pinned: bool            # User can pin favorite threads
    created_at: datetime
    updated_at: datetime
```

### 8.2 Message

```python
class Message:
    id: str                    # UUID v4
    thread_id: str             # FK → Thread.id
    role: str                  # "user" | "assistant"
    content: str               # Text content (markdown for assistant)
    attached_file_ids: list[str]  # Files uploaded with this message
    sql_query: str | None      # SQL query that was executed (if any)
    sql_result: dict | None    # Tabular result data (if any)
    sources: list[Source]      # RAG source citations (if any)
    thinking_steps: list[str]  # Agent intermediate reasoning steps
    created_at: datetime
```

### 8.3 Document

```python
class Document:
    id: str                    # UUID v4
    filename: str              # Original filename
    file_type: str             # "pdf" | "csv" | "txt" | "docx"
    file_size: int             # Size in bytes
    file_path: str             # Storage path (local or S3 key)
    upload_source: str         # "sidebar" | "chat"
    thread_id: str | None      # Set if uploaded in-chat
    status: str                # "uploading" | "processing" | "ready" | "error"
    error_message: str | None  # Error details if status is "error"
    chunk_count: int           # Number of vector chunks created
    created_at: datetime
```

### 8.4 Source (Embedded in Message)

```python
class Source:
    document_id: str           # FK → Document.id
    document_name: str         # Display name
    page: int | None           # Page number (for PDFs)
    chunk_index: int           # Which chunk was matched
    snippet: str               # Relevant text excerpt
    relevance_score: float     # Similarity score (0-1)
```

### 8.5 TypeScript Types (Frontend)

```typescript
// lib/types.ts

interface Thread {
  id: string;
  title: string;
  mode: "sql" | "rag" | "hybrid";
  attachedDocIds: string[];
  isPinned: boolean;
  createdAt: string;
  updatedAt: string;
  lastMessage?: string; // Preview snippet for sidebar
}

interface Message {
  id: string;
  threadId: string;
  role: "user" | "assistant";
  content: string;
  attachedFileIds: string[];
  sqlQuery?: string;
  sqlResult?: Record<string, unknown>[];
  sources?: Source[];
  thinkingSteps?: string[];
  createdAt: string;
}

interface Document {
  id: string;
  filename: string;
  fileType: string;
  fileSize: number;
  uploadSource: "sidebar" | "chat";
  threadId?: string;
  status: "uploading" | "processing" | "ready" | "error";
  errorMessage?: string;
  chunkCount: number;
  createdAt: string;
}

interface Source {
  documentId: string;
  documentName: string;
  page?: number;
  chunkIndex: number;
  snippet: string;
  relevanceScore: number;
}
```

---

## 9. API Contract

### 9.1 Chat

#### `POST /chat/stream`

Stream a response from the agent for a given question within a thread.

**Request:**

```json
{
  "thread_id": "uuid-string",
  "question": "How many albums are in the database?",
  "attached_doc_ids": ["doc-uuid-1"],
  "mode": "sql"
}
```

**Response:** `text/event-stream` (SSE)

```
event: step
data: {"type": "thinking", "content": "Checking database tables..."}

event: step
data: {"type": "sql_query", "content": "SELECT COUNT(*) AS total FROM Album"}

event: step
data: {"type": "sql_result", "content": [{"total": 347}]}

event: answer
data: {"type": "final", "content": "There are **347** albums in the database."}

event: done
data: {"message_id": "msg-uuid"}
```

### 9.2 Threads

| Method   | Endpoint        | Description                    | Request Body        | Response                  |
| -------- | --------------- | ------------------------------ | ------------------- | ------------------------- |
| `GET`    | `/threads`      | List all threads               | -                   | `Thread[]`                |
| `POST`   | `/threads`      | Create new thread              | `{ title?, mode? }` | `Thread`                  |
| `GET`    | `/threads/{id}` | Get thread with messages       | -                   | `Thread & { messages[] }` |
| `PATCH`  | `/threads/{id}` | Update thread (rename, mode)   | `{ title?, mode? }` | `Thread`                  |
| `DELETE` | `/threads/{id}` | Delete thread and its messages | -                   | `204 No Content`          |

### 9.3 Documents

| Method   | Endpoint                  | Description                     | Request Body          | Response               |
| -------- | ------------------------- | ------------------------------- | --------------------- | ---------------------- |
| `GET`    | `/documents`              | List all documents              | -                     | `Document[]`           |
| `POST`   | `/documents`              | Upload document(s)              | `multipart/form-data` | `Document[]`           |
| `GET`    | `/documents/{id}`         | Get document metadata           | -                     | `Document`             |
| `DELETE` | `/documents/{id}`         | Delete document + vector chunks | -                     | `204 No Content`       |
| `GET`    | `/documents/{id}/preview` | Preview first N text chunks     | `?chunks=5`           | `{ chunks: string[] }` |

### 9.4 Database Info

| Method | Endpoint                  | Description                  | Response                               |
| ------ | ------------------------- | ---------------------------- | -------------------------------------- |
| `GET`  | `/database/schema`        | Get all tables and columns   | `{ tables: TableSchema[] }`            |
| `GET`  | `/database/tables/{name}` | Get sample rows from a table | `{ columns: string[], rows: any[][] }` |

---

## 10. Document Ingestion Pipeline (RAG)

### Pipeline Flow

```
                    ┌─────────────────┐
                    │  File Upload     │
                    │  (PDF/CSV/TXT/   │
                    │   DOCX)          │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  File Storage    │
                    │  Save to disk/S3 │
                    │  Update status:  │
                    │  "processing"    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Document Loader │
                    │  (LangChain)     │
                    │                  │
                    │  PDF → PyPDF     │
                    │  CSV → CSVLoader │
                    │  TXT → TextLoader│
                    │  DOCX → Docx2txt │
                    └────────┬────────┘
                             │
                    ┌────────▼─────────────┐
                    │  Text Splitter         │
                    │  RecursiveCharacter     │
                    │  TextSplitter           │
                    │                         │
                    │  chunk_size: 1000       │
                    │  chunk_overlap: 200     │
                    └────────┬───────────────┘
                             │
                    ┌────────▼────────┐
                    │  Embedding Model │
                    │  Google's         │
                    │  text-embedding-  │
                    │  004              │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Vector Store    │
                    │  ChromaDB        │
                    │                  │
                    │  Store chunks +  │
                    │  embeddings +    │
                    │  metadata        │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Update Status   │
                    │  "ready"         │
                    │  Set chunk_count │
                    └─────────────────┘
```

### Chunking Strategy

| Parameter       | Value                       | Rationale                                         |
| --------------- | --------------------------- | ------------------------------------------------- |
| `chunk_size`    | 1000                        | Balances context richness vs. embedding precision |
| `chunk_overlap` | 200                         | Prevents losing context at chunk boundaries       |
| `separators`    | `["\n\n", "\n", ". ", " "]` | Respects document structure                       |

### Metadata Stored Per Chunk

```python
{
    "document_id": "uuid",
    "filename": "report.pdf",
    "page": 3,                    # For PDFs
    "chunk_index": 7,
    "total_chunks": 24,
    "upload_source": "sidebar",   # or "chat"
    "thread_id": "uuid" | None    # If uploaded in-chat
}
```

---

## 11. Thread Memory & Conversation Management

### Implementation: LangGraph SqliteSaver

The thread memory is handled by LangGraph's built-in checkpoint system. This is the most natural integration with the existing `agent.stream()` pattern.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Initialize once at app startup
memory = SqliteSaver.from_conn_string("threads.db")

# Agent creation includes memory
agent = create_agent(model, tools, system_prompt=system_prompt, checkpointer=memory)

# Every call passes thread_id via config
for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    config={"configurable": {"thread_id": thread_id}},
    stream_mode="values",
):
    # LangGraph automatically loads + saves conversation history
    response = step["messages"][-1]
```

### What This Provides

- **Automatic history loading** -- When a user returns to a thread, all previous messages are restored.
- **No manual message management** -- LangGraph handles serialization/deserialization.
- **Context window management** -- Can be configured to trim old messages when context gets too long.
- **Checkpointing** -- Each agent step is checkpointed, enabling replay and debugging.

### Thread Lifecycle

```
Create Thread → First Message → Agent Response → ... → N Messages → Delete Thread
     │                │              │                                     │
     ▼                ▼              ▼                                     ▼
  DB: INSERT      Memory:        Memory:                              DB: DELETE
  thread row      save user      save assistant                       thread +
                  message        message                              messages +
                                                                      memory
```

---

## 12. UI/UX Design

### 12.1 Sidebar Behavior

| Behavior             | Description                                                 |
| -------------------- | ----------------------------------------------------------- |
| **Collapsible**      | Toggle button collapses sidebar to icon-only rail           |
| **Resizable**        | Drag handle on right edge to resize width                   |
| **Section Collapse** | Chats and Documents sections independently collapsible      |
| **Thread Search**    | Real-time filter on thread titles                           |
| **Context Menu**     | Right-click on thread/doc for actions (rename, delete, pin) |
| **Active Indicator** | Currently open thread highlighted in sidebar                |
| **Auto-Title**       | New threads auto-titled from first user message             |

### 12.2 Chat Input Behavior

| Behavior                   | Description                                            |
| -------------------------- | ------------------------------------------------------ |
| **Auto-Resize**            | Textarea grows with content (max 6 lines, then scroll) |
| **Send Shortcut**          | Enter to send, Shift+Enter for new line                |
| **Attach Files**           | 📎 button opens file picker (multi-select)             |
| **File Chips**             | Attached files shown as removable chips below input    |
| **Mode Toggle**            | Dropdown to select SQL / RAG / Hybrid mode             |
| **Disabled While Loading** | Input and send disabled while agent is responding      |

### 12.3 Agent Message Features

| Feature                | Description                                               |
| ---------------------- | --------------------------------------------------------- |
| **Streaming Text**     | Characters appear in real-time as agent generates         |
| **SQL Blocks**         | SQL queries in syntax-highlighted blocks with copy button |
| **Result Tables**      | Query results in sortable, scrollable tables              |
| **Source Cards**       | RAG citations with doc name, page, snippet, relevance     |
| **Thinking Accordion** | Expandable section showing agent reasoning steps          |
| **Copy Button**        | Copy full response to clipboard                           |
| **Retry Button**       | Re-run the same query with current context                |

---

## 13. Technology Stack

### Backend

| Category        | Technology                       | Version | Purpose                          |
| --------------- | -------------------------------- | ------- | -------------------------------- |
| Runtime         | Python                           | 3.13+   | Primary backend language         |
| Web Framework   | FastAPI                          | 0.115+  | HTTP API with async support      |
| ASGI Server     | Uvicorn                          | 0.34+   | Production-grade ASGI server     |
| LLM Framework   | LangChain                        | 0.3+    | Agent orchestration              |
| Agent Framework | LangGraph                        | 0.2+    | Stateful agent with memory       |
| LLM Provider    | Google Gemini 2.5 Flash          | -       | Language model                   |
| SQL Toolkit     | langchain-community              | 0.3+    | SQL database tools               |
| Vector Store    | ChromaDB                         | 0.5+    | Document embeddings (Phase 2)    |
| Embeddings      | Google text-embedding-004        | -       | Document vectorization (Phase 2) |
| ORM             | SQLAlchemy                       | 2.0+    | Database ORM for app metadata    |
| Validation      | Pydantic                         | 2.0+    | Request/response validation      |
| Database        | SQLite (dev) / PostgreSQL (prod) | -       | App data + target query DB       |
| File Storage    | Local FS (dev) / S3 (prod)       | -       | Uploaded document storage        |
| Environment     | python-dotenv                    | -       | Environment variable management  |

### Frontend

| Category         | Technology               | Version | Purpose                          |
| ---------------- | ------------------------ | ------- | -------------------------------- |
| Framework        | Next.js (App Router)     | 15+     | React framework with SSR         |
| Language         | TypeScript               | 5.0+    | Type-safe frontend code          |
| UI Library       | shadcn/ui                | latest  | Composable UI components         |
| Styling          | Tailwind CSS             | 4.0+    | Utility-first CSS                |
| State Management | Zustand                  | 5.0+    | Lightweight global state         |
| Chat/Streaming   | Vercel AI SDK (`ai`)     | 4.0+    | `useChat` hook for SSE streaming |
| Data Tables      | TanStack Table           | 8.0+    | Sortable, virtualized tables     |
| Markdown         | react-markdown           | 9.0+    | Render agent markdown responses  |
| Syntax Highlight | react-syntax-highlighter | 15.0+   | SQL query display                |
| File Upload      | react-dropzone           | 14.0+   | Drag-and-drop file upload        |
| Icons            | Lucide React             | latest  | Consistent icon set              |
| HTTP Client      | Native fetch             | -       | API calls from route handlers    |

### DevOps

| Category         | Technology              | Purpose                          |
| ---------------- | ----------------------- | -------------------------------- |
| Containerization | Docker + Docker Compose | Consistent dev/prod environments |
| Reverse Proxy    | Nginx (optional)        | Production routing               |
| CI/CD            | GitHub Actions          | Automated testing and deployment |

---

## 14. Storage Strategy

| Data                         | Dev Storage           | Prod Storage            | Reason                   |
| ---------------------------- | --------------------- | ----------------------- | ------------------------ |
| Target SQL Database          | SQLite file           | PostgreSQL              | Query target             |
| App Metadata (threads, docs) | SQLite file           | PostgreSQL              | Relational data          |
| Thread Memory/Checkpoints    | LangGraph SqliteSaver | LangGraph PostgresSaver | Built-in agent memory    |
| Uploaded Documents (raw)     | Local `uploads/` dir  | AWS S3 / GCS            | Binary file storage      |
| Document Embeddings          | ChromaDB (local)      | Pinecone / pgvector     | Vector similarity search |
| Environment Config           | `.env` file           | Secret Manager          | Secure config management |

---

## 15. Security Considerations

| Concern                | Mitigation                                                                     |
| ---------------------- | ------------------------------------------------------------------------------ |
| **SQL Injection**      | Agent prompt explicitly forbids DML; LangChain toolkit is read-only by default |
| **API Key Exposure**   | Keys stored in `.env` (gitignored); frontend never sees keys directly          |
| **File Upload Safety** | Validate file types, enforce size limits (e.g., 50MB), scan for malware        |
| **CORS**               | Next.js route handlers proxy to backend; no direct browser→FastAPI calls       |
| **Rate Limiting**      | Implement per-user rate limits on `/chat/stream` and `/documents`              |
| **Input Validation**   | Pydantic models validate all request bodies                                    |
| **Authentication**     | Add JWT/OAuth layer before production (out of scope for Phase 1)               |
| **Data Isolation**     | Thread data scoped by user ID when auth is added                               |

---

<!-- ## 16. Phased Rollout Plan

### Phase 1: Web-Enabled SQL Agent (4-6 weeks)

**Goal:** Replace CLI with a web UI; streaming SQL chat with thread memory.

| Task                                         | Effort    |
|----------------------------------------------|-----------|
| Set up FastAPI backend with `/chat/stream`   | 1 week    |
| Implement thread memory (LangGraph)          | 0.5 week  |
| Thread CRUD API endpoints                    | 0.5 week  |
| Set up Next.js project with shadcn/ui        | 0.5 week  |
| Build Sidebar (threads list)                 | 1 week    |
| Build Chat UI (messages, input, streaming)   | 1.5 weeks |
| SQL result table rendering                   | 0.5 week  |
| Integration testing + polish                 | 0.5 week  |

**Deliverable:** Working web app that replaces CLI. Users can chat with SQL database, see streamed responses, and manage conversation threads.

### Phase 2: Document Management + RAG (4-6 weeks)

**Goal:** Add document upload, vector storage, and RAG capabilities.

| Task                                         | Effort    |
|----------------------------------------------|-----------|
| Document upload API + storage                | 1 week    |
| Document ingestion pipeline (load/split/embed)| 1.5 weeks|
| ChromaDB integration                         | 0.5 week  |
| RAG agent creation                           | 1 week    |
| Hybrid agent (SQL + RAG)                     | 0.5 week  |
| Sidebar document section UI                  | 1 week    |
| In-chat file upload UI                       | 0.5 week  |
| Source citations in agent messages            | 0.5 week  |
| Testing + polish                             | 0.5 week  |

**Deliverable:** Users can upload documents, ask questions about them, and get answers that combine SQL data with document knowledge.

### Phase 3: Production Hardening (2-4 weeks)

**Goal:** Make the system production-ready.

| Task                                         | Effort    |
|----------------------------------------------|-----------|
| Authentication (JWT / OAuth)                 | 1 week    |
| PostgreSQL migration                         | 0.5 week  |
| S3 file storage migration                    | 0.5 week  |
| Docker Compose setup                         | 0.5 week  |
| CI/CD pipeline (GitHub Actions)              | 0.5 week  |
| Rate limiting + error handling               | 0.5 week  |
| Monitoring + logging                         | 0.5 week  |

**Deliverable:** Production-deployed application with authentication, scalable storage, and monitoring.

---

## 17. Risks & Mitigations

| Risk                                        | Impact | Likelihood | Mitigation                                                     |
|---------------------------------------------|--------|------------|----------------------------------------------------------------|
| LLM generates harmful SQL                   | High   | Low        | Prompt engineering + read-only DB connection + DML blocking     |
| Large document uploads slow down system      | Medium | Medium     | Background processing queue; file size limits; chunking config  |
| LangChain/LangGraph breaking changes        | Medium | Medium     | Pin dependency versions; integration tests                     |
| Vector search returns irrelevant results     | Medium | Medium     | Tunable similarity thresholds; re-ranking; user feedback loop  |
| API key costs escalate                       | Medium | Medium     | Rate limiting; caching frequent queries; model fallback        |
| Thread memory grows unbounded                | Low    | Medium     | Configurable context window; message trimming strategy         |
| Concurrent users overwhelm single agent      | High   | Low (early)| Agent pool; async FastAPI; horizontal scaling in Phase 3       |

--- -->

## Appendix A: Environment Variables

```bash
# backend/.env.example

# --- LLM Configuration ---
GOOGLE_API_KEY=your-google-api-key-here
MODEL_NAME=google_genai:gemini-2.5-flash

# --- Database ---
DATABASE_URL=sqlite:///./Chinook.db
# For production: postgresql://user:pass@host:5432/dbname

# --- Vector Store (Phase 2) ---
CHROMA_PERSIST_DIR=./chroma_data
# For production Pinecone:
# PINECONE_API_KEY=your-pinecone-key
# PINECONE_INDEX=sql-agent-docs

# --- File Storage ---
UPLOAD_DIR=./uploads
# For production S3:
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# S3_BUCKET=sql-agent-uploads

# --- App Settings ---
TOP_K=5
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,csv,txt,docx
```

```bash
# frontend/.env.local.example

NEXT_PUBLIC_APP_NAME=SQL Agent
BACKEND_URL=http://localhost:8000
```

---

## Appendix B: Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/chroma_data:/app/chroma_data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local
    depends_on:
      backend:
        condition: service_healthy
```

---

_Document prepared for architectural review. All timelines are estimates and subject to team capacity and scope refinement._
