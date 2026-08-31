export type AuditEventSummary = {
  action: string;
  actor_user_id: number | null;
  created_at: string;
  details: string | null;
  id: number;
  target_id: string | null;
  target_type: string;
};

export type AuditEventFilters = {
  action: string;
  actorUserId: string;
  createdFrom: string;
  createdTo: string;
  limit: string;
  projectId: string;
};
