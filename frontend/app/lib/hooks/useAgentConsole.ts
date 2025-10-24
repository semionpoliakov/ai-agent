"use client";

import { useMutation } from "@tanstack/react-query";
import { nanoid } from "nanoid";
import { useCallback, useMemo, useState, type Dispatch, type SetStateAction } from "react";

import { submitAgentQuery } from "@/lib/api";
import type { AgentHistoryEntry, AgentQueryPayload } from "@/types/agent";
import { useStableUserId } from "./useStableUserId";

interface UseAgentConsoleResult {
  question: string;
  setQuestion: Dispatch<SetStateAction<string>>;
  isQuestionValid: boolean;
  error: string | null;
  resetError: () => void;
  messages: AgentHistoryEntry[];
  isSubmitting: boolean;
  handleSubmit: (question: string) => void;
}

export function useAgentConsole(): UseAgentConsoleResult {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<AgentHistoryEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  const userId = useStableUserId();

  const mutation = useMutation({
    mutationFn: (payload: AgentQueryPayload) => submitAgentQuery(payload),
    onSuccess: (data, variables) => {
      setMessages((prev) => [
        {
          id: nanoid(),
          question: variables.question,
          response: data,
          createdAt: Date.now(),
        },
        ...prev,
      ]);
      setQuestion("");
      setError(null);
    },
    onError: (err: unknown) => {
      const message = err instanceof Error ? err.message : "Something went wrong";
      setError(message);
    },
  });

  const isQuestionValid = useMemo(() => question.trim().length >= 3, [question]);

  const handleSubmit = useCallback(
    (rawQuestion: string) => {
      const trimmed = rawQuestion.trim();
      if (!trimmed) {
        setError("Please enter a question about your marketing data.");
        return;
      }

      mutation.mutate({ question: trimmed, userId });
    },
    [mutation, userId],
  );

  const resetError = useCallback(() => setError(null), []);

  return {
    question,
    setQuestion,
    isQuestionValid,
    error,
    resetError,
    messages,
    isSubmitting: mutation.isPending,
    handleSubmit,
  };
}
