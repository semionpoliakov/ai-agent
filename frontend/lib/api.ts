import type { QueryPayload, QueryResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function postQuery(payload: QueryPayload, signal?: AbortSignal): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    signal,
    credentials: "omit",
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(body.detail ?? "Failed to fetch data");
  }

  return (await res.json()) as QueryResponse;
}
