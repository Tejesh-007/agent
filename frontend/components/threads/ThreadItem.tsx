"use client";

import { useRouter } from "next/navigation";
import { MessageSquare, Trash2 } from "lucide-react";
import { useThreadStore } from "@/lib/stores/thread-store";
import { cn } from "@/lib/utils";

interface ThreadItemProps {
  thread: {
    id: string;
    title: string;
    mode: string;
    updated_at: string;
  };
}

export function ThreadItem({ thread }: ThreadItemProps) {
  const router = useRouter();
  const { activeThreadId, setActiveThread, deleteThread } = useThreadStore();
  const isActive = activeThreadId === thread.id;

  const handleClick = () => {
    setActiveThread(thread.id);
    router.push(`/chat/${thread.id}`);
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    await deleteThread(thread.id);
    if (isActive) {
      router.push("/");
    }
  };

  return (
    <div
      onClick={handleClick}
      role="button"
      className={cn(
        "w-full flex items-center gap-2 rounded-lg px-2 py-2 text-left text-sm transition-colors group cursor-pointer overflow-hidden",
        isActive
          ? "bg-accent text-accent-foreground"
          : "hover:bg-accent/50 text-foreground"
      )}
    >
      <MessageSquare className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
      <span className="flex-1 min-w-0 truncate">{thread.title}</span>
      <span
        role="button"
        tabIndex={0}
        onClick={handleDelete}
        className="flex-shrink-0 p-1 rounded hover:bg-red-500/20 transition-colors"
        title="Delete chat"
      >
        <Trash2 className="w-4 h-4 text-red-500" />
      </span>
    </div>
  );
}
