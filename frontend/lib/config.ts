/**
 * Centralized configuration — values come from environment variables.
 * Server-side env vars (no NEXT_PUBLIC_ prefix) are safe for API routes.
 */
export const BACKEND_URL =
  process.env.BACKEND_URL || "http://localhost:8000";
