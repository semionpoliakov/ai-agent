"use client";

import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { nanoid } from "nanoid";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Skeleton } from "../components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { rateLimiter } from "../lib/rate-limit";
import { postQuery } from "../lib/api";
import { useDebounce } from "../lib/use-debounce";
import type { AgentMessage, QueryResponse } from "../lib/types";
import { Download, Eye, Send } from "lucide-react";
import { DataTable } from "../components/data-table";

function downloadCsv(rows: Array<Record<string, string | number | null>>, question: string) {
  if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const csvRows = [headers.join(",")];

  rows.forEach((row) => {
    const line = headers
      .map((header) => {
        const value = row[header];
        if (value === null || value === undefined) return "";
        const stringified = typeof value === "number" ? String(value) : String(value);
        return `"${stringified.replace(/"/g, '""')}"`;
      })
      .join(",");
    csvRows.push(line);
  });

  const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${question.slice(0, 32).replace(/\s+/g, "-") || "query"}.csv`);
  link.click();
  URL.revokeObjectURL(url);
}

export default function HomePage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const debouncedQuestion = useDebounce(question, 400);
  const queryClient = useQueryClient();

  const userId = useMemo(() => {
    if (typeof crypto !== "undefined" && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return nanoid();
  }, []);

  const mutation = useMutation({
    mutationKey: ["agent-query"],
    mutationFn: async (payload: { question: string; user_id: string }) => postQuery(payload),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(["agent-query", variables.question], data);
      setMessages((prev) => [
        {
          id: nanoid(),
          question: variables.question,
          response: data,
          createdAt: Date.now(),
        },
        ...prev,
      ]);
      setError(null);
    },
    onError: (err: unknown) => {
      const message = err instanceof Error ? err.message : "Something went wrong";
      setError(message);
    },
  });

  const isQuestionValid = debouncedQuestion.trim().length >= 3;

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      setError("Please enter a question about your marketing data.");
      return;
    }
    if (!rateLimiter.allow()) {
      setError("Slow down – too many requests. Please retry in a few seconds.");
      return;
    }

    const cached = queryClient.getQueryData<QueryResponse>(["agent-query", trimmed]);
    if (cached) {
      setMessages((prev) => [
        { id: nanoid(), question: trimmed, response: cached, createdAt: Date.now() },
        ...prev,
      ]);
      setError(null);
      return;
    }

    mutation.mutate({ question: trimmed, user_id: userId });
  };

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-10 lg:px-0">
      <section className="space-y-4">
        <h1 className="text-3xl font-semibold tracking-tight">Marketing Analytics Copilot</h1>
        <p className="text-sm text-muted-foreground">
          Ask natural-language questions about your Facebook Ads and Google Ads performance. The
          agent will generate ClickHouse SQL, execute the query, and summarise the results for you.
        </p>
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
              onChange={(event) => setQuestion(event.target.value)}
              autoComplete="off"
            />
          </div>
          <div className="flex items-center justify-between gap-3">
            <span className="text-xs text-muted-foreground">
              Cached answers appear instantly. Remaining client-side requests:{" "}
              {rateLimiter.remaining()}
            </span>
            <Button
              type="submit"
              disabled={!isQuestionValid || mutation.isPending}
              className="inline-flex items-center gap-2"
            >
              <Send size={16} /> Ask agent
            </Button>
          </div>
        </form>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
      </section>

      {mutation.isPending ? (
        <Card>
          <CardHeader>
            <CardTitle>Working on it…</CardTitle>
          </CardHeader>
          <CardContent className="gap-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      ) : null}

      <section className="space-y-4">
        {messages.length === 0 && !mutation.isPending ? (
          <Card>
            <CardHeader>
              <CardTitle>Example prompts</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc space-y-2 pl-5 text-sm text-muted-foreground">
                <li>Show spend, clicks, CTR and ROAS by ad source for the last 7 days.</li>
                <li>
                  What are the spend quantiles and unique campaign count in the US for the past
                  quarter?
                </li>
                <li>Highlight campaigns with the highest ROAS week over week.</li>
              </ul>
            </CardContent>
          </Card>
        ) : null}

        {messages.map((message) => (
          <Card key={message.id} className="space-y-4">
            <CardHeader>
              <CardTitle className="text-base">{message.question}</CardTitle>
              <p className="text-sm text-muted-foreground">
                Answered{" "}
                {new Date(message.createdAt).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-foreground">{message.response.summary}</p>
              <div className="flex flex-wrap gap-3 pt-2">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="inline-flex items-center gap-2">
                      <Eye size={16} /> View SQL
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogTitle>Generated SQL</DialogTitle>
                    <DialogDescription className="text-sm text-muted-foreground">
                      Review the ClickHouse query before running it elsewhere.
                    </DialogDescription>
                    <pre className="scrollbar-thin max-h-72 overflow-auto rounded-md bg-muted/40 p-4 text-xs">
                      {message.response.sql}
                    </pre>
                  </DialogContent>
                </Dialog>
                <Button
                  variant="outline"
                  className="inline-flex items-center gap-2"
                  onClick={() => downloadCsv(message.response.data, message.question)}
                  disabled={!message.response.data.length}
                >
                  <Download size={16} /> Download CSV
                </Button>
              </div>
              <div className="pt-4">
                <DataTable rows={message.response.data} />
              </div>
            </CardContent>
          </Card>
        ))}
      </section>
    </main>
  );
}
