"use client";

import { Bot, ChevronDown, ChevronRight, Copy, Check } from "lucide-react";
import { useState } from "react";
import { SQLCodeBlock } from "./SQLCodeBlock";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";

interface AgentMessageProps {
  content: string;
  sqlQuery?: string;
  sqlResult?: string;
  thinkingSteps?: string[];
  isStreaming?: boolean;
}

export function AgentMessage({
  content,
  sqlQuery,
  sqlResult,
  thinkingSteps,
  isStreaming,
}: AgentMessageProps) {
  const [showThinking, setShowThinking] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex gap-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
        <Bot className="w-4 h-4 text-primary" />
      </div>
      <div className="flex-1 space-y-3 min-w-0">
        {/* Thinking steps accordion */}
        {thinkingSteps && thinkingSteps.length > 0 && (
          <>
            <button
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setShowThinking(!showThinking)}
            >
              {showThinking ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
              {thinkingSteps.length} thinking step
              {thinkingSteps.length > 1 ? "s" : ""}
            </button>
            {showThinking && (
              <div className="text-xs text-muted-foreground bg-muted/50 rounded-lg p-3 space-y-1">
                {thinkingSteps.map((step, i) => (
                  <p key={i}>{step}</p>
                ))}
              </div>
            )}
          </>
        )}

        {/* SQL Query block */}
        {sqlQuery && <SQLCodeBlock code={sqlQuery} />}

        {/* SQL Result */}
        {sqlResult && (
          <div className="bg-muted/50 rounded-lg p-3 overflow-x-auto">
            <p className="text-xs font-medium text-muted-foreground mb-1">
              Query Result
            </p>
            <pre className="text-xs whitespace-pre-wrap font-mono">
              {sqlResult}
            </pre>
          </div>
        )}

        {/* Main markdown content */}
        {content && (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}

        {/* Streaming indicator */}
        {isStreaming && !content && (
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span className="text-xs text-muted-foreground">Thinking...</span>
          </div>
        )}

        {/* Copy button */}
        {content && !isStreaming && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs text-muted-foreground"
            onClick={handleCopy}
          >
            {copied ? (
              <Check className="w-3 h-3 mr-1" />
            ) : (
              <Copy className="w-3 h-3 mr-1" />
            )}
            {copied ? "Copied" : "Copy"}
          </Button>
        )}
      </div>
    </div>
  );
}
