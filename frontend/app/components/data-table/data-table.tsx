"use client";

import { memo, useMemo } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { AgentDataCell, AgentDataRow } from "@/types/agent";

export interface DataTableProps {
  rows: AgentDataRow[];
}

function formatCell(value: AgentDataCell): string {
  if (Array.isArray(value)) {
    return value.map((item) => formatCell(item ?? null)).join(", ");
  }
  if (value === null || value === undefined) {
    return "—";
  }
  if (typeof value === "number") {
    const fraction = Number.isInteger(value) ? 0 : 2;
    return value.toLocaleString(undefined, {
      minimumFractionDigits: fraction,
      maximumFractionDigits: fraction,
    });
  }
  return value;
}

function InnerDataTable({ rows }: DataTableProps) {
  const columns = useMemo(() => {
    if (!rows.length) return [] as string[];
    return Object.keys(rows[0]);
  }, [rows]);

  if (!rows.length) {
    return <p className="text-sm text-muted-foreground">No rows returned for this query.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead key={column}>{column}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, index) => (
            <TableRow key={index}>
              {columns.map((column) => (
                <TableCell key={column}>{formatCell(row[column] ?? null)}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

InnerDataTable.displayName = "DataTable";

export const DataTable = memo(InnerDataTable);
DataTable.displayName = "DataTable";
