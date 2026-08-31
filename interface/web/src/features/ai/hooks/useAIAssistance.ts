import { useEffect, useEffectEvent, useState } from "react";

import {
  applyAIAnalysisProposal,
  createAIAnalysisProposal,
  createAuthorizedContextManifest,
  getAIAssistanceStatus,
  listAIAssistanceModels,
  reviewAIAnalysisProposal,
} from "../../../shared/api/ai";
import type {
  AIAnalysisProposal,
  AIAnalysisProposalApplication,
  AIAnalysisProposalReview,
  AIAssistanceModelCatalog,
  AIAssistanceStatus,
  AuthorizedContextManifest,
  CreateAuthorizedContextManifestInput,
} from "../../../shared/types/ai";
import type { ProjectSummary } from "../../../shared/types/project";

type AIAssistanceState = {
  application: AIAnalysisProposalApplication | null;
  errorMessage: string | null;
  isApplying: boolean;
  isCreatingProposal: boolean;
  isLoadingStatus: boolean;
  isReviewing: boolean;
  manifest: AuthorizedContextManifest | null;
  message: string | null;
  modelCatalog: AIAssistanceModelCatalog | null;
  proposal: AIAnalysisProposal | null;
  review: AIAnalysisProposalReview | null;
  status: AIAssistanceStatus | null;
};

const initialState: AIAssistanceState = {
  application: null,
  errorMessage: null,
  isApplying: false,
  isCreatingProposal: false,
  isLoadingStatus: false,
  isReviewing: false,
  manifest: null,
  message: null,
  modelCatalog: null,
  proposal: null,
  review: null,
  status: null,
};

function buildErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}

export function useAIAssistance(
  token: string | null,
  selectedProject: ProjectSummary | null,
  onAppliedProject: (project: ProjectSummary) => void,
) {
  const [state, setState] = useState<AIAssistanceState>(initialState);
  const canUseAIAssistance = token !== null && selectedProject !== null;

  const refreshStatus = useEffectEvent(async () => {
    if (token === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoadingStatus: true,
    }));

    try {
      const [status, modelCatalog] = await Promise.all([
        getAIAssistanceStatus(token),
        listAIAssistanceModels(token),
      ]);
      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isLoadingStatus: false,
        modelCatalog,
        status,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: buildErrorMessage(error, "Unable to load AI assistance status."),
        isLoadingStatus: false,
      }));
    }
  });

  useEffect(() => {
    if (!canUseAIAssistance) {
      setState(initialState);
      return;
    }

    setState((currentState) => ({
      ...currentState,
      application: null,
      errorMessage: null,
      manifest: null,
      message: null,
      proposal: null,
      review: null,
    }));
    void refreshStatus();
  }, [canUseAIAssistance, refreshStatus, selectedProject?.id]);

  const createProposal = useEffectEvent(
    async (
      manifestInput: Omit<CreateAuthorizedContextManifestInput, "project_id">,
      userInstructions: string | null,
    ) => {
      if (token === null || selectedProject === null) {
        return;
      }

      setState((currentState) => ({
        ...currentState,
        application: null,
        errorMessage: null,
        isCreatingProposal: true,
        manifest: null,
        message: null,
        proposal: null,
        review: null,
      }));

      try {
        const manifest = await createAuthorizedContextManifest(token, {
          ...manifestInput,
          project_id: selectedProject.id,
        });
        const proposal = await createAIAnalysisProposal(token, {
          manifest_id: manifest.id,
          user_instructions: userInstructions,
        });
        setState((currentState) => ({
          ...currentState,
          errorMessage: null,
          isCreatingProposal: false,
          manifest,
          message: `Proposal ${proposal.id} created for review.`,
          proposal,
        }));
      } catch (error) {
        setState((currentState) => ({
          ...currentState,
          errorMessage: buildErrorMessage(error, "Unable to create an AI proposal."),
          isCreatingProposal: false,
        }));
      }
    },
  );

  const reviewProposal = useEffectEvent(
    async (decision: "approved" | "rejected", reviewerNotes: string | null) => {
      if (token === null || state.proposal === null) {
        return;
      }

      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isReviewing: true,
      }));

      try {
        const review = await reviewAIAnalysisProposal(token, state.proposal.id, {
          decision,
          reviewer_notes: reviewerNotes,
        });
        setState((currentState) => ({
          ...currentState,
          errorMessage: null,
          isReviewing: false,
          message: `Proposal ${decision}.`,
          review,
        }));
      } catch (error) {
        setState((currentState) => ({
          ...currentState,
          errorMessage: buildErrorMessage(error, "Unable to review the AI proposal."),
          isReviewing: false,
        }));
      }
    },
  );

  const applyProposal = useEffectEvent(async () => {
    if (token === null || state.proposal === null) {
      return;
    }
    const proposalId = state.proposal.id;

    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isApplying: true,
    }));

    try {
      const application = await applyAIAnalysisProposal(token, proposalId, {
        confirm_file_write: true,
        confirm_mapping_persistence: true,
      });
      onAppliedProject(application.project);
      setState((currentState) => ({
        ...currentState,
        application,
        errorMessage: null,
        isApplying: false,
        message: `Proposal ${proposalId} applied.`,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: buildErrorMessage(error, "Unable to apply the AI proposal."),
        isApplying: false,
      }));
    }
  });

  return {
    ...state,
    applyProposal,
    canUseAIAssistance,
    createProposal,
    refreshStatus,
    reviewProposal,
  };
}
