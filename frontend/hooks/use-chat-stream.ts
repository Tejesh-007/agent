"use client";

import { useState, useCallback } from "react";
import type { Message } from "@/lib/types";

export function useChatStream() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = useCallback(
    async (threadId: string, question: string, mode: string = "auto") => {
      setIsStreaming(true);

      // Add user message immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: question,
      };

      // Create placeholder for agent message
      const agentMessageId = `agent-${Date.now()}`;
      const agentMessage: Message = {
        id: agentMessageId,
        role: "assistant",
        content: "",
        thinkingSteps: [],
      };

      setMessages((prev) => [...prev, userMessage, agentMessage]);

      try {
        // Send mode as null if "auto" to trigger backend classification
        const payload = {
          thread_id: threadId,
          question,
          mode: mode === "auto" ? null : mode,
        };
        
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          let currentEvent = "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              currentEvent = line.slice(7).trim();
            } else if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));

                setMessages((prev) =>
                  prev.map((msg) => {
                    if (msg.id !== agentMessageId) return msg;

                    if (
                      currentEvent === "step" &&
                      data.type === "thinking"
                    ) {
                      return {
                        ...msg,
                        thinkingSteps: [
                          ...(msg.thinkingSteps || []),
                          data.content,
                        ],
                      };
                    } else if (
                      currentEvent === "step" &&
                      data.type === "sql_query"
                    ) {
                      return { ...msg, sqlQuery: data.content };
                    } else if (
                      currentEvent === "step" &&
                      data.type === "sql_result"
                    ) {
                      return { ...msg, sqlResult: data.content };
                    } else if (
                      currentEvent === "step" &&
                      data.type === "source"
                    ) {
                      return { ...msg, sources: data.content };
                    } else if (currentEvent === "answer") {
                      return { ...msg, content: data.content };
                    }

                    return msg;
                  })
                );
              } catch {
                // Ignore malformed JSON
              }
            }
          }
        }
      } catch (error) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === agentMessageId
              ? {
                  ...msg,
                  content:
                    "Error: Failed to get response from agent. Make sure the backend is running.",
                }
              : msg
          )
        );
      } finally {
        setIsStreaming(false);
      }
    },
    []
  );

  return { messages, setMessages, isStreaming, sendMessage };
}
