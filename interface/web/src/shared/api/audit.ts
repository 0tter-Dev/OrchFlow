import { requestJson } from "./client";
import type { AuditEventSummary } from "../types/audit";

export function listAuditEvents(token: string, limit = 25): Promise<AuditEventSummary[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  return requestJson<AuditEventSummary[]>(`/audit/events?${params.toString()}`, { token });
}
