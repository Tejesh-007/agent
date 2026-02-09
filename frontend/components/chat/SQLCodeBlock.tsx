"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { Button } from "@/components/ui/button";

interface SQLCodeBlockProps {
  code: string;
}

export function SQLCodeBlock({ code }: SQLCodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative rounded-lg overflow-hidden border">
      <div className="flex items-center justify-between bg-muted px-3 py-1.5">
        <span className="text-xs font-medium text-muted-foreground">SQL</span>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 text-xs"
          onClick={handleCopy}
        >
          {copied ? (
            <Check className="w-3 h-3" />
          ) : (
            <Copy className="w-3 h-3" />
          )}
        </Button>
      </div>
      <SyntaxHighlighter
        language="sql"
        style={oneDark}
        customStyle={{ margin: 0, borderRadius: 0, fontSize: "0.8rem" }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}
