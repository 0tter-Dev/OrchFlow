import { requestJson } from "./client";
import type {
  AIAnalysisProposal,
  AIAnalysisProposalApplication,
  AIAnalysisProposalReview,
  AIAssistanceModelCatalog,
  AIAssistanceStatus,
  AuthorizedContextManifest,
  CreateAIAnalysisProposalInput,
  CreateAuthorizedContextManifestInput,
} from "../types/ai";

export function getAIAssistanceStatus(token: string): Promise<AIAssistanceStatus> {
  return requestJson<AIAssistanceStatus>("/ai/status", { token });
}

export function listAIAssistanceModels(token: string): Promise<AIAssistanceModelCatalog> {
  return requestJson<AIAssistanceModelCatalog>("/ai/models", { token });
}

export function createAuthorizedContextManifest(
  token: string,
  payload: CreateAuthorizedContextManifestInput,
): Promise<AuthorizedContextManifest> {
  return requestJson<AuthorizedContextManifest>("/ai/context-manifests", {
    body: payload,
    method: "POST",
    token,
  });
}

export function createAIAnalysisProposal(
  token: string,
  payload: CreateAIAnalysisProposalInput,
): Promise<AIAnalysisProposal> {
  return requestJson<AIAnalysisProposal>("/ai/analysis-proposals", {
    body: payload,
    method: "POST",
    token,
  });
}

export function reviewAIAnalysisProposal(
  token: string,
  proposalId: number,
  payload: { decision: "approved" | "rejected"; reviewer_notes?: string | null },
): Promise<AIAnalysisProposalReview> {
  return requestJson<AIAnalysisProposalReview>(`/ai/analysis-proposals/${proposalId}/review`, {
    body: payload,
    method: "POST",
    token,
  });
}

export function applyAIAnalysisProposal(
  token: string,
  proposalId: number,
  payload: { confirm_file_write: boolean; confirm_mapping_persistence: boolean },
): Promise<AIAnalysisProposalApplication> {
  return requestJson<AIAnalysisProposalApplication>(`/ai/analysis-proposals/${proposalId}/apply`, {
    body: payload,
    method: "POST",
    token,
  });
}
