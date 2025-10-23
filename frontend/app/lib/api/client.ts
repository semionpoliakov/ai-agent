import { env } from "@/config/env";
import { ApiError, buildApiError } from "./errors";
import type { ZodSchema } from "zod";

interface RequestOptions<TSchema> {
  path: string;
  schema: ZodSchema<TSchema>;
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
  cache?: RequestCache;
}

export async function request<TResponse>({
  path,
  schema,
  method = "GET",
  body,
  headers,
  signal,
  cache = "no-store",
}: RequestOptions<TResponse>): Promise<TResponse> {
  const url = `${env.apiBaseUrl}${path}`;
  const isJsonBody = body !== undefined;
  let response: Response;

  try {
    response = await fetch(url, {
      method,
      body: isJsonBody ? JSON.stringify(body) : undefined,
      headers: {
        ...(isJsonBody ? { "Content-Type": "application/json" } : null),
        ...headers,
      },
      credentials: "omit",
      signal,
      cache,
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw error;
    }
    const reason = error instanceof Error ? error.message : "unknown error";
    throw new ApiError(`Unable to reach API (${reason})`, { status: 0 });
  }

  const responseText = await response.text();
  const parsedBody = responseText ? safeJsonParse(responseText) : null;

  if (!response.ok) {
    throw buildApiError(response.status, parsedBody ?? responseText);
  }

  return schema.parse(parsedBody);
}

function safeJsonParse(value: string): unknown {
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}
