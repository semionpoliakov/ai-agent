import { z } from "zod";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

const envSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.string().url().optional(),
});

let apiBaseUrl: string;

try {
  const parsed = envSchema.parse({
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  });

  apiBaseUrl = parsed.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;

  if (!parsed.NEXT_PUBLIC_API_BASE_URL && process.env.NODE_ENV === "production") {
    throw new Error("NEXT_PUBLIC_API_BASE_URL must be defined in production builds.");
  }

  if (!parsed.NEXT_PUBLIC_API_BASE_URL && process.env.NODE_ENV !== "production") {
    console.warn(`[env] NEXT_PUBLIC_API_BASE_URL not set. Using fallback: ${DEFAULT_API_BASE_URL}`);
  }
} catch (err) {
  throw new Error(`Invalid environment configuration: ${(err as Error).message}`);
}

export const env = {
  apiBaseUrl,
} as const;
