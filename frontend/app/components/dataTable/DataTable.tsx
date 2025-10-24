"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { AgentDataCell, AgentDataRow } from "@/types/agent";
import { memo } from "react";

interface DataTableProps {
  rows: AgentDataRow[];
}

function formatCell(value: AgentDataCell): string {
  if (Array.isArray(value)) return value.map((item) => formatCell(item ?? null)).join(", ");
  if (value == null) return "—";
  if (typeof value === "number") {
    const fraction = Number.isInteger(value) ? 0 : 2;
    return value.toLocaleString(undefined, {
      minimumFractionDigits: fraction,
      maximumFractionDigits: fraction,
    });
  }
  return String(value);
}

function InnerDataTable({ rows }: DataTableProps) {
  if (!rows.length)
    return (
      <div className="overflow-x-auto">
        <Table>
          <TableBody>
            <TableRow>
              <TableCell className="text-center text-sm text-muted-foreground">
                No rows returned
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    );

  const columns = Object.keys(rows[0]);

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
          {rows.map((row, i) => (
            <TableRow key={i}>
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

export const DataTable = memo(InnerDataTable);
DataTable.displayName = "DataTable";
