export type CanonicalLifecycleAction = "status" | "start" | "stop" | "restart";

export type ProjectActionMapping = {
  canonical_action: CanonicalLifecycleAction;
  configured_by_user_id: number;
  script_label: string;
  source: "user_defined" | "imported" | "ai_approved";
};

export type LifecycleConfigurationHealth = "complete" | "partial" | "blocked";

export type LifecycleFunctionConfiguration = {
  canonical_action: CanonicalLifecycleAction;
  description: string;
  preferred_script_identifier: string;
  script_label: string | null;
  state: "configured" | "undefined" | "unconfigured";
};

export type ProjectSummary = {
  action_mappings: ProjectActionMapping[];
  created_by_user_id: number;
  description: string | null;
  id: number;
  lifecycle_configuration_health: LifecycleConfigurationHealth;
  lifecycle_function_configurations: LifecycleFunctionConfiguration[];
  lifecycle_script_path: string;
  owner_user_ids: number[];
  project_root_path: string;
  reference_name: string;
};

export type ProjectReloadResult = {
  changed_actions: CanonicalLifecycleAction[];
  current_lifecycle_configuration_health: LifecycleConfigurationHealth;
  previous_lifecycle_configuration_health: LifecycleConfigurationHealth;
  project: ProjectSummary;
};

export type ProjectUnlinkResult = {
  lifecycle_script_path: string;
  local_files_preserved: boolean;
  project_id: number;
  project_root_path: string;
  reference_name: string;
  registry_entry_removed: boolean;
  unlinked_owner_user_id: number | null;
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

export type ProjectUpdateInput = {
  description?: string | null;
  lifecycle_script_path?: string;
  mappings?: ProjectRegistrationMappingInput[];
  project_root_path?: string;
  reference_name?: string;
  unconfigured_actions?: CanonicalLifecycleAction[];
};

export type ProjectLifecycleConfigurationInput = {
  mappings: ProjectRegistrationMappingInput[];
  unconfigured_actions: CanonicalLifecycleAction[];
};

export type RuntimeProcessSnapshot = {
  cpu_seconds: number | null;
  memory_bytes: number | null;
  name: string;
  pid: number;
  started_at: string | null;
};

export type RuntimeInspectionSnapshot = {
  application_reachable: boolean | null;
  application_url: string | null;
  inspected_at: string;
  known_port: number | null;
  process_snapshots: RuntimeProcessSnapshot[];
  project_id: number;
  status: string;
  status_reason: string;
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
