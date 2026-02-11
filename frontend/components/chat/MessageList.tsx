"use client";

import { useEffect, useRef } from "react";
import { UserMessage } from "./UserMessage";
import { AgentMessage } from "./AgentMessage";
import { StreamingIndicator } from "./StreamingIndicator";
import type { Message } from "@/lib/types";

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
}

export function MessageList({ messages, isStreaming }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        <p>Send a message to start chatting</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.map((message) =>
          message.role === "user" ? (
            <UserMessage key={message.id} content={message.content} />
          ) : (
            <AgentMessage
              key={message.id}
              content={message.content}
              sqlQuery={message.sqlQuery}
              sqlResult={message.sqlResult}
              thinkingSteps={message.thinkingSteps}
              sources={message.sources}
              isStreaming={
                isStreaming && message === messages[messages.length - 1]
              }
            />
          )
        )}
        {isStreaming &&
          messages.length > 0 &&
          !messages[messages.length - 1]?.content &&
          !messages[messages.length - 1]?.sqlQuery && <StreamingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
