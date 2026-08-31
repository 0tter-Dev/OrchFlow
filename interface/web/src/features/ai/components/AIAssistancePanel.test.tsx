import { fireEvent, render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import { describe, expect, it, vi } from "vitest";

import type { AIAnalysisProposal } from "../../../shared/types/ai";
import type { ProjectSummary } from "../../../shared/types/project";
import { AIAssistancePanel } from "./AIAssistancePanel";

const selectedProject: ProjectSummary = {
  action_mappings: [],
  created_by_user_id: 1,
  description: "Demo",
  id: 7,
  lifecycle_configuration_health: "partial",
  lifecycle_function_configurations: [],
  lifecycle_script_path: "E:/Projects/demo/control.bat",
  owner_user_ids: [1],
  project_root_path: "E:/Projects/demo",
  reference_name: "demo-project",
};

const proposal: AIAnalysisProposal = {
  action_mappings: [
    {
      canonical_action: "status",
      rationale: "Detected canonical status.",
      script_label: "STATUS",
    },
  ],
  candidate_script_content: "@echo off\r\nif /I \"%~1\"==\"STATUS\" echo ok",
  created_at: "2026-08-31T03:20:00+00:00",
  id: 12,
  intended_operation: "improve_lifecycle_script",
  lifecycle_strategy: "Use first-argument dispatch.",
  manifest_id: 11,
  project_id: 7,
  requested_by_user_id: 1,
  runtime_hints: ["APP_PORT=8000"],
  selected_model: "ollama/llama3",
  warnings: ["Review before applying."],
};

function renderPanel(overrides: Partial<ComponentProps<typeof AIAssistancePanel>> = {}) {
  return render(
    <AIAssistancePanel
      canUseAIAssistance
      errorMessage={null}
      isApplying={false}
      isCreatingProposal={false}
      isLoadingStatus={false}
      isReviewing={false}
      message={null}
      modelIds={["ollama/llama3"]}
      onApplyProposal={vi.fn()}
      onCreateProposal={vi.fn()}
      onRefreshStatus={vi.fn()}
      onReviewProposal={vi.fn()}
      proposal={null}
      readyForRequests
      reviewDecision={null}
      selectedProject={selectedProject}
      statusMessage="AI assistance is ready."
      {...overrides}
    />,
  );
}

describe("AIAssistancePanel", () => {
  it("creates reviewable proposals with explicit manifest inputs", () => {
    const onCreateProposal = vi.fn();
    renderPanel({ onCreateProposal });

    fireEvent.change(screen.getByLabelText("Reviewer instructions"), {
      target: { value: "Prefer the existing control.bat style." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create proposal" }));

    expect(onCreateProposal).toHaveBeenCalledWith({
      excludePatterns: [".env", ".venv", "node_modules", "dist"],
      includePatterns: ["*"],
      intendedOperation: "improve_lifecycle_script",
      maxFileSizeBytes: 65536,
      maxTotalBytes: 262144,
      selectedModel: "ollama/llama3",
      userInstructions: "Prefer the existing control.bat style.",
    });
  });

  it("requires both confirmations before applying a proposal", () => {
    const onApplyProposal = vi.fn();
    renderPanel({ onApplyProposal, proposal, reviewDecision: "approved" });

    const applyButton = screen.getByRole("button", { name: "Apply approved proposal" });
    expect(applyButton).toBeDisabled();

    fireEvent.click(screen.getByLabelText("Confirm lifecycle script file write"));
    expect(applyButton).toBeDisabled();

    fireEvent.click(screen.getByLabelText("Confirm mapping persistence"));
    fireEvent.click(applyButton);

    expect(onApplyProposal).toHaveBeenCalled();
  });

  it("requires approval before applying a proposal", () => {
    const onApplyProposal = vi.fn();
    renderPanel({ onApplyProposal, proposal });

    fireEvent.click(screen.getByLabelText("Confirm lifecycle script file write"));
    fireEvent.click(screen.getByLabelText("Confirm mapping persistence"));

    expect(screen.getByRole("button", { name: "Apply approved proposal" })).toBeDisabled();
    expect(onApplyProposal).not.toHaveBeenCalled();
  });

  it("disables proposal creation when AI assistance is not ready", () => {
    renderPanel({ readyForRequests: false });

    expect(screen.getByRole("button", { name: "Create proposal" })).toBeDisabled();
  });
});
