import { NextRequest } from "next/server";
import { BACKEND_URL } from "@/lib/config";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const response = await fetch(`${BACKEND_URL}/threads/${id}`);
  if (!response.ok) {
    return Response.json({ error: "Thread not found" }, { status: 404 });
  }
  const data = await response.json();
  return Response.json(data);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const body = await request.json();
  const response = await fetch(`${BACKEND_URL}/threads/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    return Response.json({ error: "Thread not found" }, { status: 404 });
  }
  const data = await response.json();
  return Response.json(data);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  await fetch(`${BACKEND_URL}/threads/${id}`, { method: "DELETE" });
  return new Response(null, { status: 204 });
}
