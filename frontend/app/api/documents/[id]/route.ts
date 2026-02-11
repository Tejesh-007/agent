import { NextRequest } from "next/server";
import { BACKEND_URL } from "@/lib/config";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const response = await fetch(`${BACKEND_URL}/documents/${id}`);
  if (!response.ok) {
    return Response.json({ error: "Document not found" }, { status: 404 });
  }
  const data = await response.json();
  return Response.json(data);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  await fetch(`${BACKEND_URL}/documents/${id}`, { method: "DELETE" });
  return new Response(null, { status: 204 });
}
