"use client";

import type { FormEvent } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface AgentQuestionFormProps {
  question: string;
  onQuestionChange: (value: string) => void;
  onSubmit: (value: string) => void;
  isQuestionValid: boolean;
  isSubmitting: boolean;
  remainingRequests: number;
}

export function AgentQuestionForm({
  question,
  onQuestionChange,
  onSubmit,
  isQuestionValid,
  isSubmitting,
  remainingRequests,
}: AgentQuestionFormProps) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit(question);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-xl border border-muted-foreground/20 bg-card p-4 shadow-sm"
    >
      <div className="flex flex-col gap-2">
        <label htmlFor="question" className="text-sm font-medium text-muted-foreground">
          Question
        </label>
        <Input
          id="question"
          name="question"
          placeholder="e.g. Compare ROAS and CTR for top campaigns in the last 30 days"
          value={question}
          onChange={(event) => onQuestionChange(event.target.value)}
          autoComplete="off"
          aria-describedby="question-hint"
          aria-invalid={question.length > 0 && !isQuestionValid ? true : undefined}
        />
      </div>
      <div className="flex items-center justify-between gap-3">
        <span id="question-hint" className="text-xs text-muted-foreground">
          Cached answers appear instantly. Remaining client-side requests: {remainingRequests}
        </span>
        <Button
          type="submit"
          disabled={!isQuestionValid || isSubmitting}
          className="inline-flex items-center gap-2"
        >
          <Send size={16} /> Ask agent
        </Button>
      </div>
    </form>
  );
}
