import { requestJson } from "./client";
import type { AuditEventFilters, AuditEventSummary } from "../types/audit";

export function listAuditEvents(
  token: string,
  filters?: Partial<AuditEventFilters>,
): Promise<AuditEventSummary[]> {
  const params = new URLSearchParams({ limit: filters?.limit || "25" });
  if (filters?.actorUserId) {
    params.set("actor_user_id", filters.actorUserId);
  }
  if (filters?.action) {
    params.set("action", filters.action);
  }
  if (filters?.projectId) {
    params.set("project_id", filters.projectId);
  }
  if (filters?.createdFrom) {
    params.set("created_from", filters.createdFrom);
  }
  if (filters?.createdTo) {
    params.set("created_to", filters.createdTo);
  }
  return requestJson<AuditEventSummary[]>(`/audit/events?${params.toString()}`, { token });
}
