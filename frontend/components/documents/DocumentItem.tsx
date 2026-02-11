"use client";

import { FileText, Trash2, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { useDocumentStore } from "@/lib/stores/document-store";
import type { Document } from "@/lib/types";

interface DocumentItemProps {
  document: Document;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "processing":
      return <Loader2 className="w-3 h-3 animate-spin text-yellow-500" />;
    case "ready":
      return <CheckCircle2 className="w-3 h-3 text-green-500" />;
    case "error":
      return <AlertCircle className="w-3 h-3 text-red-500" />;
    default:
      return null;
  }
}

export function DocumentItem({ document }: DocumentItemProps) {
  const { deleteDocument } = useDocumentStore();

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    await deleteDocument(document.id);
  };

  return (
    <div className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm hover:bg-accent/50 overflow-hidden">
      <FileText className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
      <div className="flex-1 min-w-0">
        <p className="truncate text-xs">{document.filename}</p>
        <p className="text-[10px] text-muted-foreground">
          {formatFileSize(document.file_size)}
          {document.status === "ready" && ` - ${document.chunk_count} chunks`}
        </p>
      </div>
      <StatusIcon status={document.status} />
      <span
        role="button"
        tabIndex={0}
        onClick={handleDelete}
        className="flex-shrink-0 p-1 rounded hover:bg-red-500/20 transition-colors"
        title="Delete document"
      >
        <Trash2 className="w-4 h-4 text-red-500" />
      </span>
    </div>
  );
}
