"use client";

import { Eye } from "lucide-react";
import { memo } from "react";

import { DataTable } from "@/components/dataTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import type { AgentHistoryEntry } from "@/types/agent";

interface AgentMessageCardProps {
  entry: AgentHistoryEntry;
}

function AgentMessageCardComponent({ entry }: AgentMessageCardProps) {
  const answeredAt = new Date(entry.createdAt).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <Card className="space-y-4">
      <CardHeader>
        <CardTitle className="text-base">{entry.question}</CardTitle>
        <p className="text-sm text-muted-foreground">Answered {answeredAt}</p>
      </CardHeader>

      <CardContent>
        <p className="text-sm leading-relaxed text-foreground">{entry.response.summary}</p>

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
                {entry.response.sql}
              </pre>
            </DialogContent>
          </Dialog>
        </div>

        <div className="pt-4">
          {entry.response.data.length ? (
            <DataTable rows={entry.response.data} />
          ) : (
            <p className="text-sm text-muted-foreground">No data returned for this query.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export const AgentMessageCard = memo(AgentMessageCardComponent);
AgentMessageCard.displayName = "AgentMessageCard";
