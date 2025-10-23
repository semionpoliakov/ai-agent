import { z } from "zod";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

const envSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z
    .string()
    .url()
    .or(z.literal(""))
    .optional(),
});

const result = envSchema.safeParse({
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

if (!result.success) {
  throw new Error(
    `Invalid environment configuration: ${result.error.issues
      .map((issue) => issue.message)
      .join(", ")}`,
  );
}

const resolvedApiBaseUrl =
  result.data.NEXT_PUBLIC_API_BASE_URL && result.data.NEXT_PUBLIC_API_BASE_URL.length > 0
    ? result.data.NEXT_PUBLIC_API_BASE_URL
    : DEFAULT_API_BASE_URL;

if (!result.data.NEXT_PUBLIC_API_BASE_URL) {
  if (process.env.NODE_ENV === "production") {
    throw new Error("NEXT_PUBLIC_API_BASE_URL must be defined in production builds.");
  }
  if (typeof console !== "undefined") {
    console.warn(
      `[env] NEXT_PUBLIC_API_BASE_URL is not set. Falling back to ${DEFAULT_API_BASE_URL}.`,
    );
  }
}

export const env = {
  apiBaseUrl: resolvedApiBaseUrl,
} as const;
