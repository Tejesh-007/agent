"use client";

import { useRef, useState } from "react";
import { Upload, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDocumentStore } from "@/lib/stores/document-store";

export function DocumentUploadButton() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { uploadDocument } = useDocumentStore();

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      await uploadDocument(file);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      // Reset file input so same file can be re-uploaded
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".pdf,.csv,.txt,.docx"
        onChange={handleFileChange}
      />
      <Button
        variant="ghost"
        size="sm"
        className="w-full justify-start gap-2 text-xs h-8"
        onClick={handleClick}
        disabled={uploading}
      >
        {uploading ? (
          <Loader2 className="w-3 h-3 animate-spin" />
        ) : (
          <Upload className="w-3 h-3" />
        )}
        {uploading ? "Uploading..." : "Upload Document"}
      </Button>
      {error && (
        <p className="text-[10px] text-red-500 px-2 mt-1">{error}</p>
      )}
    </div>
  );
}
