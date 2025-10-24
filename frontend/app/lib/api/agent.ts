import type { AgentQueryPayload, AgentQueryRequestDTO, AgentQueryResponse } from "@/types/agent";
import { request } from "./client";
import { agentQueryRequestSchema, agentQueryResponseSchema } from "./schemas";

export async function submitAgentQuery(
  payload: AgentQueryPayload,
  signal?: AbortSignal,
): Promise<AgentQueryResponse> {
  const requestBody: AgentQueryRequestDTO = agentQueryRequestSchema.parse({
    question: payload.question,
    user_id: payload.userId,
  });

  return request({
    path: "/api/v1/query",
    method: "POST",
    body: requestBody,
    schema: agentQueryResponseSchema,
    signal,
    cache: "no-store",
  });
}
