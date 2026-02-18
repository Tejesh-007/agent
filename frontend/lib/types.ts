export interface Thread {
  id: string;
  title: string;
  mode: "sql" | "rag" | "hybrid";
  created_at: string;
  updated_at: string;
}

export interface Source {
  documentId: string;
  documentName: string;
  page?: number;
  chunkIndex: number;
  snippet: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sqlQuery?: string;
  sqlResult?: string;
  thinkingSteps?: string[];
  sources?: string; // Raw retrieved context from RAG
}

export interface ThreadDetail extends Thread {
  messages: {
    id: string;
    role: string;
    content: string;
    sql_query?: string;
    sql_result?: string;
    created_at: string;
  }[];
}

export interface ChatRequest {
  thread_id: string;
  question: string;
  mode?: string | null;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: "processing" | "ready" | "error";
  chunk_count: number;
  error_message?: string;
  created_at: string;
}
