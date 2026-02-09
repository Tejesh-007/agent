"use client";

import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useThreadStore } from "@/lib/stores/thread-store";

export function NewChatButton() {
  const router = useRouter();
  const { createThread } = useThreadStore();

  const handleClick = async () => {
    const thread = await createThread();
    router.push(`/chat/${thread.id}`);
  };

  return (
    <Button onClick={handleClick} className="w-full gap-2" variant="outline">
      <Plus className="w-4 h-4" />
      New Chat
    </Button>
  );
}
