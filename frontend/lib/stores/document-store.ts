import { create } from "zustand";
import type { Document } from "@/lib/types";

interface DocumentStore {
  documents: Document[];
  loading: boolean;

  fetchDocuments: () => Promise<void>;
  uploadDocument: (file: File) => Promise<Document>;
  deleteDocument: (id: string) => Promise<void>;
}

export const useDocumentStore = create<DocumentStore>((set) => ({
  documents: [],
  loading: false,

  fetchDocuments: async () => {
    set({ loading: true });
    try {
      const res = await fetch("/api/documents");
      if (res.ok) {
        const documents = await res.json();
        set({ documents, loading: false });
      } else {
        set({ loading: false });
      }
    } catch {
      set({ loading: false });
    }
  },

  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/api/documents", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }

    const doc = await res.json();
    set((state) => ({ documents: [doc, ...state.documents] }));
    return doc;
  },

  deleteDocument: async (id: string) => {
    await fetch(`/api/documents/${id}`, { method: "DELETE" });
    set((state) => ({
      documents: state.documents.filter((d) => d.id !== id),
    }));
  },
}));
