import { NextRequest } from "next/server";
import { BACKEND_URL } from "@/lib/config";

export async function GET() {
  const response = await fetch(`${BACKEND_URL}/documents`);
  const data = await response.json();
  return Response.json(data);
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();

  const response = await fetch(`${BACKEND_URL}/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }));
    return Response.json(error, { status: response.status });
  }

  const data = await response.json();
  return Response.json(data, { status: 201 });
}
