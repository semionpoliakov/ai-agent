"use client";

import { Button } from "@/components/ui/button";
import { useEffect } from "react";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main
      role="alert"
      aria-live="assertive"
      className="mx-auto flex min-h-[60vh] w-full max-w-2xl flex-col items-center justify-center gap-4 text-center"
    >
      <h2 className="text-2xl font-semibold">Something went wrong</h2>
      <p className="text-sm text-muted-foreground">
        The agent could not complete your request. Please retry or adjust your question.
      </p>
      <Button onClick={reset}>Try again</Button>
    </main>
  );
}
