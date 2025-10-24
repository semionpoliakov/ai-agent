"use client";

import { useCallback } from "react";

import { useAgentConsole } from "@/lib/hooks/useAgentConsole";
import { AgentEmptyState } from "./AgentEmptyState";
import { AgentLoadingState } from "./AgentLoadingState";
import { AgentMessageCard } from "./AgentMessageCard";
import { AgentQuestionForm } from "./AgentQuestionForm";

export function AgentConsole() {
  const {
    question,
    setQuestion,
    isQuestionValid,
    messages,
    error,
    resetError,
    isSubmitting,
    handleSubmit,
  } = useAgentConsole();

  const handleQuestionChange = useCallback(
    (value: string) => {
      if (error) {
        resetError();
      }
      setQuestion(value);
    },
    [error, resetError, setQuestion],
  );

  return (
    <section className="space-y-4">
      <AgentQuestionForm
        question={question}
        onQuestionChange={handleQuestionChange}
        onSubmit={handleSubmit}
        isQuestionValid={isQuestionValid}
        isSubmitting={isSubmitting}
      />

      {error ? (
        <p
          role="alert"
          aria-live="polite"
          aria-atomic="true"
          className="rounded-md border border-destructive/40 bg-destructive/10 px-4 py-2 text-sm text-destructive"
        >
          {error}
        </p>
      ) : null}

      {isSubmitting ? <AgentLoadingState /> : null}

      {messages.length === 0 && !isSubmitting ? <AgentEmptyState /> : null}

      {messages.map((entry) => (
        <AgentMessageCard key={entry.id} entry={entry} />
      ))}
    </section>
  );
}
