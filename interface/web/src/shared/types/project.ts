export type CanonicalLifecycleAction = "status" | "start" | "stop" | "restart";

export type ProjectActionMapping = {
  canonical_action: CanonicalLifecycleAction;
  configured_by_user_id: number;
  script_label: string;
  source: "user_defined" | "imported" | "ai_approved";
};

export type ProjectSummary = {
  action_mappings: ProjectActionMapping[];
  created_by_user_id: number;
  description: string | null;
  id: number;
  lifecycle_script_path: string;
  owner_user_ids: number[];
  project_root_path: string;
  reference_name: string;
};

export type ProjectRegistrationMappingInput = {
  canonical_action: CanonicalLifecycleAction;
  script_label: string;
  source?: "user_defined" | "imported" | "ai_approved";
};

export type ProjectRegistrationInput = {
  description?: string | null;
  lifecycle_script_path: string;
  mappings: ProjectRegistrationMappingInput[];
  project_root_path: string;
  reference_name: string;
};

export type RuntimeProcessSnapshot = {
  cpu_seconds: number | null;
  memory_bytes: number | null;
  name: string;
  pid: number;
  started_at: string | null;
};

export type RuntimeInspectionSnapshot = {
  application_url: string | null;
  known_port: number | null;
  process_snapshots: RuntimeProcessSnapshot[];
  project_id: number;
  status: string;
  uptime_seconds: number | null;
};

export type LifecycleExecutionSnapshot = {
  canonical_action: CanonicalLifecycleAction;
  command_identifier: string;
  exit_code: number;
  project_id: number;
  runtime_status: string | null;
  stderr: string;
  stdout: string;
  succeeded: boolean;
};
