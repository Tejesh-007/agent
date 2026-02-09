import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET() {
  const response = await fetch(`${BACKEND_URL}/threads`);
  const data = await response.json();
  return Response.json(data);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const response = await fetch(`${BACKEND_URL}/threads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  return Response.json(data, { status: 201 });
}
