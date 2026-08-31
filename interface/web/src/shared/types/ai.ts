import type { ProjectRegistrationMappingInput, ProjectSummary } from "./project";

export type AIAssistanceStatus = {
  api_key_configured: boolean;
  base_url: string;
  default_model: string;
  enabled: boolean;
  message: string;
  mode: string;
  provider: string;
  ready_for_requests: boolean;
  sdk_available: boolean;
  status: "disabled" | "configured" | "misconfigured";
  timeout_seconds: number;
};

export type AIAssistanceModel = {
  id: string;
  owned_by: string | null;
};

export type AIAssistanceModelCatalog = {
  base_url: string;
  default_model: string;
  enabled: boolean;
  message: string;
  mode: string;
  models: AIAssistanceModel[];
  provider: string;
  supports_discovery: boolean;
};

export type AuthorizedContextManifest = {
  created_at: string;
  exclude_patterns: string[];
  excluded_paths: string[];
  id: number;
  ignored_paths: string[];
  include_patterns: string[];
  included_paths: string[];
  intended_operation: "improve_lifecycle_script" | "generate_lifecycle_script";
  max_file_size_bytes: number;
  max_total_bytes: number;
  project_id: number;
  project_root_path: string;
  requested_by_user_id: number;
  secret_filter_rules: string[];
  selected_model: string;
  total_included_bytes: number;
};

export type ProposedLifecycleActionMapping = {
  canonical_action: ProjectRegistrationMappingInput["canonical_action"];
  rationale: string | null;
  script_label: string;
};

export type AIAnalysisProposal = {
  action_mappings: ProposedLifecycleActionMapping[];
  candidate_script_content: string;
  created_at: string;
  id: number;
  intended_operation: "improve_lifecycle_script" | "generate_lifecycle_script";
  lifecycle_strategy: string;
  manifest_id: number;
  project_id: number;
  requested_by_user_id: number;
  runtime_hints: string[];
  selected_model: string;
  warnings: string[];
};

export type AIAnalysisProposalReview = {
  created_at: string;
  decision: "approved" | "rejected";
  id: number;
  project_id: number;
  proposal_id: number;
  reviewer_notes: string | null;
  reviewer_user_id: number;
  validation_errors: string[];
  validation_status: "valid" | "invalid";
};

export type AIAnalysisProposalApplication = {
  applied_by_user_id: number;
  created_at: string;
  id: number;
  lifecycle_script_path: string;
  persisted_mappings: ProposedLifecycleActionMapping[];
  project: ProjectSummary;
  project_id: number;
  proposal_id: number;
};

export type CreateAuthorizedContextManifestInput = {
  exclude_patterns: string[];
  include_patterns: string[];
  intended_operation: "improve_lifecycle_script" | "generate_lifecycle_script";
  max_file_size_bytes: number;
  max_total_bytes: number;
  project_id: number;
  selected_model: string;
};

export type CreateAIAnalysisProposalInput = {
  manifest_id: number;
  user_instructions?: string | null;
};
