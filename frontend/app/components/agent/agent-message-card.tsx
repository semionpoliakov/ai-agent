"use client";

import dynamic from "next/dynamic";
import { memo } from "react";
import { Download, Eye } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { downloadCsv } from "@/lib/utils/download-csv";
import type { AgentHistoryEntry } from "@/types/agent";

const DataTable = dynamic(async () => (await import("@/components/data-table")).DataTable, {
  ssr: false,
  loading: () => (
    <div className="space-y-2">
      <Skeleton className="h-6 w-32" />
      <Skeleton className="h-40 w-full" />
    </div>
  ),
});

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
          <Button
            variant="outline"
            className="inline-flex items-center gap-2"
            onClick={() => downloadCsv(entry.response.data, entry.question)}
            disabled={!entry.response.data.length}
          >
            <Download size={16} /> Download CSV
          </Button>
        </div>
        <div className="pt-4">
          <DataTable rows={entry.response.data} />
        </div>
      </CardContent>
    </Card>
  );
}

const AgentMessageCardMemo = memo(AgentMessageCardComponent);
AgentMessageCardMemo.displayName = "AgentMessageCard";

export const AgentMessageCard = AgentMessageCardMemo;
