import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { ProjectSummary, RuntimeInspectionSnapshot } from "../../../shared/types/project";
import { ProjectOnboardingPanel } from "./ProjectOnboardingPanel";

const completeProject: ProjectSummary = {
  action_mappings: [],
  created_by_user_id: 1,
  description: "Demo",
  id: 7,
  lifecycle_configuration_health: "complete",
  lifecycle_function_configurations: [
    {
      canonical_action: "status",
      description: "Report status",
      preferred_script_identifier: "STATUS",
      script_label: "STATUS",
      state: "configured",
    },
    {
      canonical_action: "start",
      description: "Start project",
      preferred_script_identifier: "START",
      script_label: "START",
      state: "configured",
    },
  ],
  lifecycle_script_path: "E:/Projects/demo/control.bat",
  owner_user_ids: [1],
  project_root_path: "E:/Projects/demo",
  reference_name: "demo-project",
};

const blockedProject: ProjectSummary = {
  ...completeProject,
  lifecycle_configuration_health: "blocked",
  lifecycle_function_configurations: completeProject.lifecycle_function_configurations.map(
    (configuration) => ({
      ...configuration,
      script_label: null,
      state: "undefined" as const,
    }),
  ),
};

const runtimeSnapshot: RuntimeInspectionSnapshot = {
  application_reachable: true,
  application_url: "http://localhost:4173",
  inspected_at: "2026-08-31T03:40:00+00:00",
  known_port: 4173,
  process_snapshots: [],
  project_id: 7,
  status: "running",
  status_reason: "APP_PORT 4173 is listening.",
  uptime_seconds: 42,
};

function renderPanel(project: ProjectSummary = completeProject) {
  const onConfigureMappings = vi.fn();
  const onRefreshRuntime = vi.fn();
  const onReloadProject = vi.fn();

  render(
    <ProjectOnboardingPanel
      isLoadingRuntime={false}
      isReloadingProject={false}
      onConfigureMappings={onConfigureMappings}
      onRefreshRuntime={onRefreshRuntime}
      onReloadProject={onReloadProject}
      project={project}
      runtimeSnapshot={runtimeSnapshot}
    />,
  );

  return { onConfigureMappings, onRefreshRuntime, onReloadProject };
}

function renderPanelWithRuntime(runtimeSnapshotOverride: RuntimeInspectionSnapshot) {
  render(
    <ProjectOnboardingPanel
      isLoadingRuntime={false}
      isReloadingProject={false}
      onConfigureMappings={vi.fn()}
      onRefreshRuntime={vi.fn()}
      onReloadProject={vi.fn()}
      project={completeProject}
      runtimeSnapshot={runtimeSnapshotOverride}
    />,
  );
}

describe("ProjectOnboardingPanel", () => {
  it("shows ready state when lifecycle and runtime signals are complete", () => {
    renderPanel();

    expect(screen.getByText("Ready")).toBeInTheDocument();
    expect(screen.getByText("Current signal: APP_PORT 4173 is listening.")).toBeInTheDocument();
  });

  it("opens lifecycle mapping guidance for blocked projects", () => {
    const { onConfigureMappings } = renderPanel(blockedProject);

    expect(screen.getByText("Blocked")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open mappings" }));

    expect(onConfigureMappings).toHaveBeenCalled();
  });

  it("marks runtime diagnostics for attention when inspection is unsupported", () => {
    renderPanelWithRuntime({
      ...runtimeSnapshot,
      status: "unsupported",
      status_reason: "No APP_PORT or APP_URL hint was found.",
    });

    expect(screen.getByText("Needs review")).toBeInTheDocument();
    expect(
      screen.getByText("Current signal: No APP_PORT or APP_URL hint was found."),
    ).toBeInTheDocument();
  });
});
