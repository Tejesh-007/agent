import { NextRequest } from "next/server";
import { BACKEND_URL } from "@/lib/config";

export async function POST(request: NextRequest) {
  const body = await request.json();

  const response = await fetch(`${BACKEND_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    return new Response(
      JSON.stringify({ error: "Backend error" }),
      { status: response.status, headers: { "Content-Type": "application/json" } }
    );
  }

  // Pipe the SSE stream through to the client
  return new Response(response.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}
