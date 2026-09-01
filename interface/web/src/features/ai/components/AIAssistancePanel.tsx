import "./AIAssistancePanel.css";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ErrorNotice } from "../../../shared/components/ErrorNotice";
import type { AIAnalysisProposal } from "../../../shared/types/ai";
import type { ProjectSummary } from "../../../shared/types/project";

type AIAssistancePanelProps = {
  canUseAIAssistance: boolean;
  errorMessage: string | null;
  isApplying: boolean;
  isCreatingProposal: boolean;
  isLoadingStatus: boolean;
  isReviewing: boolean;
  message: string | null;
  modelIds: string[];
  onApplyProposal: () => void;
  onCreateProposal: (input: {
    excludePatterns: string[];
    includePatterns: string[];
    intendedOperation: "improve_lifecycle_script" | "generate_lifecycle_script";
    maxFileSizeBytes: number;
    maxTotalBytes: number;
    selectedModel: string;
    userInstructions: string | null;
  }) => void;
  onRefreshStatus: () => void;
  onReviewProposal: (decision: "approved" | "rejected", reviewerNotes: string | null) => void;
  proposal: AIAnalysisProposal | null;
  readyForRequests: boolean;
  reviewDecision: "approved" | "rejected" | null;
  selectedProject: ProjectSummary | null;
  statusMessage: string | null;
};

function splitPatterns(value: string, fallback: string[]): string[] {
  const patterns = value
    .split(",")
    .map((pattern) => pattern.trim())
    .filter((pattern) => pattern.length > 0);
  return patterns.length > 0 ? patterns : fallback;
}

function renderProposal(proposal: AIAnalysisProposal) {
  const mappings =
    proposal.action_mappings.length === 0
      ? "none"
      : proposal.action_mappings
          .map((mapping) => `${mapping.canonical_action}: ${mapping.script_label}`)
          .join("\n");
  return [
    `strategy: ${proposal.lifecycle_strategy}`,
    `runtime_hints: ${proposal.runtime_hints.join(", ") || "none"}`,
    `warnings: ${proposal.warnings.join(", ") || "none"}`,
    "",
    "action_mappings:",
    mappings,
    "",
    "candidate_script_content:",
    proposal.candidate_script_content,
  ].join("\n");
}

export function AIAssistancePanel({
  canUseAIAssistance,
  errorMessage,
  isApplying,
  isCreatingProposal,
  isLoadingStatus,
  isReviewing,
  message,
  modelIds,
  onApplyProposal,
  onCreateProposal,
  onRefreshStatus,
  onReviewProposal,
  proposal,
  readyForRequests,
  reviewDecision,
  selectedProject,
  statusMessage,
}: AIAssistancePanelProps) {
  const [confirmFileWrite, setConfirmFileWrite] = useState(false);
  const [confirmMappingPersistence, setConfirmMappingPersistence] = useState(false);
  const [excludePatterns, setExcludePatterns] = useState(".env, .venv, node_modules, dist");
  const [includePatterns, setIncludePatterns] = useState("*");
  const [intendedOperation, setIntendedOperation] = useState<
    "improve_lifecycle_script" | "generate_lifecycle_script"
  >("improve_lifecycle_script");
  const [maxFileSizeBytes, setMaxFileSizeBytes] = useState("65536");
  const [maxTotalBytes, setMaxTotalBytes] = useState("262144");
  const [reviewerNotes, setReviewerNotes] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [userInstructions, setUserInstructions] = useState("");

  const effectiveSelectedModel = selectedModel || modelIds[0] || "";
  const canCreateProposal =
    canUseAIAssistance &&
    readyForRequests &&
    effectiveSelectedModel.length > 0 &&
    !isCreatingProposal;
  const canApplyProposal =
    proposal !== null &&
    reviewDecision === "approved" &&
    confirmFileWrite &&
    confirmMappingPersistence &&
    !isApplying &&
    !isReviewing;

  useEffect(() => {
    if (modelIds.length === 0) {
      return;
    }
    setSelectedModel((currentModel) => currentModel || modelIds[0]);
  }, [modelIds]);

  function submitProposal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canCreateProposal) {
      return;
    }
    onCreateProposal({
      excludePatterns: splitPatterns(excludePatterns, []),
      includePatterns: splitPatterns(includePatterns, ["*"]),
      intendedOperation,
      maxFileSizeBytes: Number(maxFileSizeBytes),
      maxTotalBytes: Number(maxTotalBytes),
      selectedModel: effectiveSelectedModel,
      userInstructions: userInstructions.trim() || null,
    });
    setConfirmFileWrite(false);
    setConfirmMappingPersistence(false);
  }

  return (
    <section className="ai-panel">
      <header className="ai-panel__header">
        <div>
          <span className="ai-panel__eyebrow">AI assistance</span>
          <h2 className="ai-panel__title">Proposal review</h2>
        </div>
        <button
          className="ai-panel__button"
          disabled={!canUseAIAssistance || isLoadingStatus}
          onClick={onRefreshStatus}
          type="button"
        >
          {isLoadingStatus ? "Checking..." : "Check status"}
        </button>
      </header>

      {selectedProject === null ? (
        <div className="ai-panel__empty">Select a project to review AI lifecycle proposals.</div>
      ) : null}

      {statusMessage !== null ? <div className="ai-panel__status">{statusMessage}</div> : null}
      {message !== null ? <div className="ai-panel__success">{message}</div> : null}
      {errorMessage !== null ? (
        <ErrorNotice
          className="ai-panel__error"
          message={errorMessage}
          title="AI assistance needs review"
        />
      ) : null}

      <form className="ai-panel__form" onSubmit={submitProposal}>
        <label>
          <span>Model</span>
          <input
            disabled={!canUseAIAssistance}
            list="ai-model-options"
            onChange={(event) => setSelectedModel(event.target.value)}
            placeholder="ollama/llama3"
            value={selectedModel}
          />
          <datalist id="ai-model-options">
            {modelIds.map((modelId) => (
              <option key={modelId} value={modelId} />
            ))}
          </datalist>
        </label>
        <label>
          <span>Operation</span>
          <select
            disabled={!canUseAIAssistance}
            onChange={(event) =>
              setIntendedOperation(
                event.target.value as "improve_lifecycle_script" | "generate_lifecycle_script",
              )
            }
            value={intendedOperation}
          >
            <option value="improve_lifecycle_script">improve_lifecycle_script</option>
            <option value="generate_lifecycle_script">generate_lifecycle_script</option>
          </select>
        </label>
        <label>
          <span>Include patterns</span>
          <input
            disabled={!canUseAIAssistance}
            onChange={(event) => setIncludePatterns(event.target.value)}
            value={includePatterns}
          />
        </label>
        <label>
          <span>Exclude patterns</span>
          <input
            disabled={!canUseAIAssistance}
            onChange={(event) => setExcludePatterns(event.target.value)}
            value={excludePatterns}
          />
        </label>
        <label>
          <span>Max file bytes</span>
          <input
            disabled={!canUseAIAssistance}
            min="1"
            onChange={(event) => setMaxFileSizeBytes(event.target.value)}
            type="number"
            value={maxFileSizeBytes}
          />
        </label>
        <label>
          <span>Max total bytes</span>
          <input
            disabled={!canUseAIAssistance}
            min="1"
            onChange={(event) => setMaxTotalBytes(event.target.value)}
            type="number"
            value={maxTotalBytes}
          />
        </label>
        <label className="ai-panel__wide">
          <span>Reviewer instructions</span>
          <textarea
            disabled={!canUseAIAssistance}
            onChange={(event) => setUserInstructions(event.target.value)}
            value={userInstructions}
          />
        </label>
        <button className="ai-panel__primary" disabled={!canCreateProposal} type="submit">
          {isCreatingProposal ? "Creating..." : "Create proposal"}
        </button>
      </form>

      {proposal !== null ? (
        <div className="ai-panel__review">
          <pre className="ai-panel__proposal">{renderProposal(proposal)}</pre>
          <label className="ai-panel__wide">
            <span>Review notes</span>
            <textarea
              onChange={(event) => setReviewerNotes(event.target.value)}
              value={reviewerNotes}
            />
          </label>
          <div className="ai-panel__actions">
            <button
              className="ai-panel__button"
              disabled={isReviewing}
              onClick={() => onReviewProposal("rejected", reviewerNotes.trim() || null)}
              type="button"
            >
              Reject
            </button>
            <button
              className="ai-panel__primary"
              disabled={isReviewing}
              onClick={() => onReviewProposal("approved", reviewerNotes.trim() || null)}
              type="button"
            >
              {isReviewing ? "Reviewing..." : "Approve"}
            </button>
          </div>
          <div className="ai-panel__confirmations">
            <label>
              <input
                checked={confirmFileWrite}
                onChange={(event) => setConfirmFileWrite(event.target.checked)}
                type="checkbox"
              />
              <span>Confirm lifecycle script file write</span>
            </label>
            <label>
              <input
                checked={confirmMappingPersistence}
                onChange={(event) => setConfirmMappingPersistence(event.target.checked)}
                type="checkbox"
              />
              <span>Confirm mapping persistence</span>
            </label>
          </div>
          <button
            className="ai-panel__primary"
            disabled={!canApplyProposal}
            onClick={onApplyProposal}
            type="button"
          >
            {isApplying ? "Applying..." : "Apply approved proposal"}
          </button>
        </div>
      ) : null}
    </section>
  );
}
