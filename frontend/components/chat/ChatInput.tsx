"use client";

import { useState, useRef, useCallback, KeyboardEvent } from "react";
import { Send, Database, FileText, Layers, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type Mode = "auto" | "sql" | "rag" | "hybrid";

interface ChatInputProps {
  onSend: (message: string, mode: Mode | undefined) => void;
  isStreaming: boolean;
}

const MODE_CONFIG: Record<Mode, { label: string; icon: React.ReactNode; description: string }> = {
  auto: {
    label: "Auto",
    icon: <Sparkles className="w-3.5 h-3.5" />,
    description: "AI picks best mode",
  },
  sql: {
    label: "SQL",
    icon: <Database className="w-3.5 h-3.5" />,
    description: "Query the database",
  },
  rag: {
    label: "RAG",
    icon: <FileText className="w-3.5 h-3.5" />,
    description: "Search documents",
  },
  hybrid: {
    label: "Hybrid",
    icon: <Layers className="w-3.5 h-3.5" />,
    description: "Database + Documents",
  },
};

export function ChatInput({ onSend, isStreaming }: ChatInputProps) {
  const [value, setValue] = useState("");
  const [mode, setMode] = useState<Mode>("auto");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isStreaming) return;
    // Send undefined for "auto" mode to trigger backend classification
    onSend(trimmed, mode === "auto" ? undefined : mode);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, isStreaming, onSend, mode]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  };

  const currentMode = MODE_CONFIG[mode];

  return (
    <div className="border-t p-4">
      <div className="max-w-3xl mx-auto flex gap-2 items-end">
        {/* Mode selector */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-11 gap-1.5 flex-shrink-0 px-3"
              disabled={isStreaming}
            >
              {currentMode.icon}
              <span className="text-xs">{currentMode.label}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            {(Object.entries(MODE_CONFIG) as [Mode, typeof currentMode][]).map(
              ([key, config]) => (
                <DropdownMenuItem
                  key={key}
                  onClick={() => setMode(key)}
                  className="gap-2"
                >
                  {config.icon}
                  <div>
                    <p className="text-sm font-medium">{config.label}</p>
                    <p className="text-xs text-muted-foreground">
                      {config.description}
                    </p>
                  </div>
                </DropdownMenuItem>
              )
            )}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Text input */}
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder={
            mode === "auto"
              ? "Ask anything - AI will route automatically..."
              : mode === "sql"
                ? "Ask about your database..."
                : mode === "rag"
                  ? "Ask about your documents..."
                  : "Ask about your database or documents..."
          }
          className="min-h-[44px] max-h-[200px] resize-none"
          rows={1}
          disabled={isStreaming}
        />

        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={!value.trim() || isStreaming}
          size="icon"
          className="h-11 w-11 flex-shrink-0"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
      <p className="text-xs text-muted-foreground text-center mt-2">
        Press Enter to send, Shift+Enter for new line
        <span className="mx-1.5">|</span>
        Mode: {currentMode.label}
      </p>
    </div>
  );
}
