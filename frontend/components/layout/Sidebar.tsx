"use client";

import { useEffect } from "react";
import { PanelLeftClose, PanelLeft, Database, Sun, Moon } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useThreadStore } from "@/lib/stores/thread-store";
import { useUIStore } from "@/lib/stores/ui-store";
import { ThreadList } from "@/components/threads/ThreadList";
import { NewChatButton } from "@/components/threads/NewChatButton";
import { DocumentSection } from "@/components/documents/DocumentSection";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const { fetchThreads } = useThreadStore();
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    fetchThreads();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      {/* Sidebar panel */}
      <div
        className={cn(
          "flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300 overflow-hidden",
          sidebarOpen ? "w-72" : "w-0"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-2 min-w-0">
            <Database className="w-5 h-5 text-primary flex-shrink-0" />
            <span className="font-semibold text-sm truncate">SQL Agent</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="h-8 w-8 flex-shrink-0"
          >
            <PanelLeftClose className="w-4 h-4" />
          </Button>
        </div>

        {/* New Chat button */}
        <div className="px-3 pb-2">
          <NewChatButton />
        </div>

        <Separator />

        {/* Thread list */}
        <div className="flex-1 overflow-hidden flex flex-col min-h-0">
          <div className="px-3 py-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-2">
              Chats
            </p>
          </div>
          <div className="flex-1 overflow-y-auto px-3">
            <ThreadList />
          </div>
        </div>

        <Separator />

        {/* Documents section */}
        <div className="overflow-hidden flex flex-col max-h-[35%] min-h-0">
          <div className="px-3 py-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-2">
              Documents
            </p>
          </div>
          <div className="flex-1 overflow-y-auto px-3 pb-2">
            <DocumentSection />
          </div>
        </div>

        <Separator />

        {/* Footer with theme toggle */}
        <div className="p-3 flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Theme</span>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 relative"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>
        </div>
      </div>

      {/* Toggle button when sidebar is collapsed */}
      {!sidebarOpen && (
        <Button
          variant="ghost"
          size="icon"
          className="fixed top-4 left-4 z-10 h-8 w-8"
          onClick={toggleSidebar}
        >
          <PanelLeft className="w-4 h-4" />
        </Button>
      )}
    </>
  );
}
