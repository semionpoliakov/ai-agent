import type { AgentDataCell, AgentDataRow } from "@/types/agent";

export function downloadCsv(rows: AgentDataRow[], question: string) {
  if (!rows.length) return;

  const headers = Object.keys(rows[0]);
  const csvRows = [headers.join(",")];

  for (const row of rows) {
    const line = headers
      .map((header) => {
        const value = row[header];
        if (value === null || value === undefined) return "";
        const stringified = serialise(value);
        return `"${stringified.replace(/"/g, '""')}"`;
      })
      .join(",");
    csvRows.push(line);
  }

  const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${slugify(question)}.csv`);
  link.click();
  URL.revokeObjectURL(url);
}

function serialise(value: AgentDataCell): string {
  if (Array.isArray(value)) {
    return value.map((item) => serialise(item ?? "")).join("; ");
  }
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "number") {
    return String(value);
  }
  return String(value);
}

function slugify(input: string): string {
  const trimmed = input.trim().slice(0, 32);
  return trimmed ? trimmed.replace(/\s+/g, "-").toLowerCase() : "query";
}
