export type AgentDataPrimitive = string | number | null;

export type AgentDataCell = AgentDataPrimitive | AgentDataPrimitive[];

export type AgentDataRow = Record<string, AgentDataCell>;

export interface AgentQueryPayload {
  question: string;
  userId: string;
}

export interface AgentQueryResponse {
  sql: string;
  data: AgentDataRow[];
  summary: string;
}

export interface AgentQueryRequestDTO {
  question: string;
  user_id: string;
}

export interface AgentQueryResponseDTO {
  sql: string;
  data: AgentDataRow[];
  summary: string;
}

export interface AgentHistoryEntry {
  id: string;
  question: string;
  response: AgentQueryResponse;
  createdAt: number;
}

export interface AgentQueryErrorShape {
  code?: string;
  detail: string;
}

export interface AgentQueryErrorPayload {
  detail?: string;
  error?: string;
  message?: string;
  status?: number;
  code?: string;
}
