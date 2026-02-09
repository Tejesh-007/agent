import { create } from "zustand";

interface Thread {
  id: string;
  title: string;
  mode: string;
  created_at: string;
  updated_at: string;
}

interface ThreadStore {
  threads: Thread[];
  activeThreadId: string | null;
  loading: boolean;

  fetchThreads: () => Promise<void>;
  createThread: (title?: string) => Promise<Thread>;
  setActiveThread: (id: string) => void;
  updateThread: (id: string, title: string) => Promise<void>;
  deleteThread: (id: string) => Promise<void>;
}

export const useThreadStore = create<ThreadStore>((set) => ({
  threads: [],
  activeThreadId: null,
  loading: false,

  fetchThreads: async () => {
    set({ loading: true });
    try {
      const res = await fetch("/api/threads");
      if (res.ok) {
        const threads = await res.json();
        set({ threads, loading: false });
      } else {
        set({ loading: false });
      }
    } catch {
      set({ loading: false });
    }
  },

  createThread: async (title?: string) => {
    const res = await fetch("/api/threads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    const thread = await res.json();
    set((state) => ({ threads: [thread, ...state.threads] }));
    return thread;
  },

  setActiveThread: (id: string) => set({ activeThreadId: id }),

  updateThread: async (id: string, title: string) => {
    await fetch(`/api/threads/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    set((state) => ({
      threads: state.threads.map((t) =>
        t.id === id ? { ...t, title } : t
      ),
    }));
  },

  deleteThread: async (id: string) => {
    await fetch(`/api/threads/${id}`, { method: "DELETE" });
    set((state) => ({
      threads: state.threads.filter((t) => t.id !== id),
      activeThreadId:
        state.activeThreadId === id ? null : state.activeThreadId,
    }));
  },
}));
