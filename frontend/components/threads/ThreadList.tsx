"use client";

import { useThreadStore } from "@/lib/stores/thread-store";
import { ThreadItem } from "./ThreadItem";
import { Skeleton } from "@/components/ui/skeleton";

export function ThreadList() {
  const { threads, loading } = useThreadStore();

  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );
  }

  if (threads.length === 0) {
    return (
      <p className="text-xs text-muted-foreground px-2 py-4">
        No chats yet. Start a new conversation!
      </p>
    );
  }

  return (
    <div className="space-y-1">
      {threads.map((thread) => (
        <ThreadItem key={thread.id} thread={thread} />
      ))}
    </div>
  );
}
