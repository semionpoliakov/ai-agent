export type QueryPayload = {
  question: string;
  user_id?: string;
};

export type QueryResponse = {
  sql: string;
  data: Array<Record<string, string | number | null>>;
  summary: string;
};

export type AgentMessage = {
  id: string;
  question: string;
  response: QueryResponse;
  createdAt: number;
};
