"use client";

import { useEffect } from "react";
import { useDocumentStore } from "@/lib/stores/document-store";
import { DocumentItem } from "./DocumentItem";
import { DocumentUploadButton } from "./DocumentUploadButton";
import { Skeleton } from "@/components/ui/skeleton";

export function DocumentSection() {
  const { documents, loading, fetchDocuments } = useDocumentStore();

  useEffect(() => {
    fetchDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-1">
      <DocumentUploadButton />

      {loading ? (
        <div className="space-y-2 mt-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-9 w-full" />
          ))}
        </div>
      ) : documents.length === 0 ? (
        <p className="text-xs text-muted-foreground px-2 py-2">
          No documents uploaded yet.
        </p>
      ) : (
        <div className="space-y-1 mt-1">
          {documents.map((doc) => (
            <DocumentItem key={doc.id} document={doc} />
          ))}
        </div>
      )}
    </div>
  );
}
