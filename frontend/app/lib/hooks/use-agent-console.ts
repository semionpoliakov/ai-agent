"use client";

import { useCallback, useMemo, useState, type Dispatch, type SetStateAction } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { nanoid } from "nanoid";

import { submitAgentQuery } from "@/lib/api";
import { rateLimiter } from "@/lib/utils/client-rate-limiter";
import type { AgentHistoryEntry, AgentQueryPayload, AgentQueryResponse } from "@/types/agent";
import { useDebounce } from "./use-debounce";
import { useStableUserId } from "./use-stable-user-id";

interface UseAgentConsoleResult {
  question: string;
  setQuestion: Dispatch<SetStateAction<string>>;
  debouncedQuestion: string;
  isQuestionValid: boolean;
  error: string | null;
  resetError: () => void;
  messages: AgentHistoryEntry[];
  isSubmitting: boolean;
  remainingRequests: number;
  handleSubmit: (question: string) => void;
}

export function useAgentConsole(): UseAgentConsoleResult {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<AgentHistoryEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuestion = useDebounce(question, 400);

  const queryClient = useQueryClient();
  const userId = useStableUserId();

  const mutation = useMutation({
    mutationKey: ["agent-query"],
    mutationFn: (payload: AgentQueryPayload) => submitAgentQuery(payload),
    onSuccess: (data, variables) => {
      queryClient.setQueryData<AgentQueryResponse>(["agent-query", variables.question], data);
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

  const isQuestionValid = useMemo(
    () => debouncedQuestion.trim().length >= 3,
    [debouncedQuestion],
  );

  const handleSubmit = useCallback(
    (rawQuestion: string) => {
      const trimmed = rawQuestion.trim();
      if (!trimmed) {
        setError("Please enter a question about your marketing data.");
        return;
      }

      const cached = queryClient.getQueryData<AgentQueryResponse>(["agent-query", trimmed]);
      if (cached) {
        setMessages((prev) => [
          {
            id: nanoid(),
            question: trimmed,
            response: cached,
            createdAt: Date.now(),
          },
          ...prev,
        ]);
        setQuestion("");
        setError(null);
        return;
      }

      if (!rateLimiter.allow()) {
        setError("Slow down – too many requests. Please retry in a few seconds.");
        return;
      }

      mutation.mutate({ question: trimmed, userId });
    },
    [mutation, queryClient, userId],
  );
  const resetError = useCallback(() => setError(null), []);

  return {
    question,
    setQuestion,
    debouncedQuestion,
    isQuestionValid,
    error,
    resetError,
    messages,
    isSubmitting: mutation.isPending,
    remainingRequests: rateLimiter.remaining(),
    handleSubmit,
  };
}
