"use client";

import { useRouter } from "next/navigation";
import { Database, MessageSquare, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useThreadStore } from "@/lib/stores/thread-store";

export default function HomePage() {
  const router = useRouter();
  const { createThread } = useThreadStore();

  const handleNewChat = async () => {
    const thread = await createThread();
    router.push(`/chat/${thread.id}`);
  };

  return (
    <div className="flex flex-1 items-center justify-center">
      <div className="max-w-md text-center space-y-6">
        <div className="mx-auto w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
          <Sparkles className="w-8 h-8 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent</h1>
          <p className="text-muted-foreground mt-2">
            Ask questions about your database/documents in natural language.
          </p>
        </div>
        <div className="flex flex-col gap-3 items-center">
          <Button size="lg" onClick={handleNewChat} className="gap-2">
            <MessageSquare className="w-4 h-4" />
            Start New Chat
          </Button>
        </div>
        <div className="grid grid-cols-3 gap-4 pt-4 text-sm text-muted-foreground">
          <div className="flex flex-col items-center gap-2">
            <Database className="w-5 h-5" />
            <span>SQL Queries</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            <span>Chat History</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Sparkles className="w-5 h-5" />
            <span>AI Powered</span>
          </div>
        </div>
      </div>
    </div>
  );
}
