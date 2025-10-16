"use client";

import { memo, useMemo } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

export type DataTableProps = {
  rows: Array<Record<string, string | number | null>>;
};

function formatCell(value: string | number | null): string {
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

export const DataTable = memo(InnerDataTable);
