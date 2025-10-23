import { z } from "zod";

const agentDataPrimitiveSchema = z.union([z.string(), z.number(), z.null()]);

export const agentDataCellSchema = z.union([
  agentDataPrimitiveSchema,
  z.array(agentDataPrimitiveSchema),
]);

export const agentDataRowSchema = z.record(agentDataCellSchema);

export const agentQueryResponseSchema = z.object({
  sql: z.string(),
  data: z.array(agentDataRowSchema),
  summary: z.string(),
});

export const agentQueryRequestSchema = z.object({
  question: z.string().min(3),
  user_id: z.string().min(1),
});

export const agentQueryErrorSchema = z.object({
  detail: z.string().optional(),
  error: z.string().optional(),
  message: z.string().optional(),
  code: z.string().optional(),
});
