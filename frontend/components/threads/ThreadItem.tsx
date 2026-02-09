"use client";

import { useRouter } from "next/navigation";
import { MessageSquare, Trash2 } from "lucide-react";
import { useThreadStore } from "@/lib/stores/thread-store";
import { Button } from "@/components/ui/button";
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
    await deleteThread(thread.id);
    if (isActive) {
      router.push("/");
    }
  };

  return (
    <button
      onClick={handleClick}
      className={cn(
        "w-full flex items-center gap-2 rounded-lg px-2 py-2 text-left text-sm transition-colors group",
        isActive
          ? "bg-accent text-accent-foreground"
          : "hover:bg-accent/50 text-foreground"
      )}
    >
      <MessageSquare className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
      <span className="flex-1 truncate">{thread.title}</span>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
        onClick={handleDelete}
      >
        <Trash2 className="w-3 h-3 text-muted-foreground" />
      </Button>
    </button>
  );
}
