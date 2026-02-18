"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import { MessageList } from "@/components/chat/MessageList";
import { ChatInput } from "@/components/chat/ChatInput";
import { useChatStream } from "@/hooks/use-chat-stream";
import { useThreadStore } from "@/lib/stores/thread-store";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function ChatPage() {
  const params = useParams();
  const threadId = params.threadId as string;
  const { messages, setMessages, isStreaming, sendMessage } = useChatStream();
  const { threads, setActiveThread, updateThread } = useThreadStore();
  const currentThread = threads.find((t) => t.id === threadId);

  useEffect(() => {
    setActiveThread(threadId);
    loadMessages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [threadId]);

  async function loadMessages() {
    try {
      const res = await fetch(`/api/threads/${threadId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.messages?.length > 0) {
          setMessages(
            data.messages.map((m: Record<string, string>) => ({
              id: m.id || `msg-${Math.random()}`,
              role: m.role,
              content: m.content,
              sqlQuery: m.sql_query,
              sqlResult: m.sql_result,
            })),
          );
        }
      }
    } catch {
      // Thread may not have messages yet
    }
  }

  async function handleSend(question: string, mode: "sql" | "rag" | "hybrid" | undefined) {
    await sendMessage(threadId, question, mode || "auto");
    // Auto-title from first message
    if (currentThread?.title === "New Chat") {
      const title = question.slice(0, 50) + (question.length > 50 ? "..." : "");
      updateThread(threadId, title);
    }
  }

  const title = currentThread?.title || "Chat";

  return (
    <div className="flex flex-col h-full">
      <div className="border-b pl-15 pr-0 py-3 flex items-center min-w-0">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <h2 className="font-semibold text-lg truncate min-w-0 flex-1">
                {title}
              </h2>
            </TooltipTrigger>
            {title.length > 50 && (
              <TooltipContent>
                <p className="max-w-md">{title}</p>
              </TooltipContent>
            )}
          </Tooltip>
        </TooltipProvider>
      </div>
      <MessageList messages={messages} isStreaming={isStreaming} />
      <ChatInput onSend={handleSend} isStreaming={isStreaming} />
    </div>
  );
}
