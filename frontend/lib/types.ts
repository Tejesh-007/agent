export interface Thread {
  id: string;
  title: string;
  mode: "sql" | "rag" | "hybrid";
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sqlQuery?: string;
  sqlResult?: string;
  thinkingSteps?: string[];
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
  mode?: string;
}
