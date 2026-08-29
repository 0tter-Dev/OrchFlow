import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { UserSummary } from "../../../shared/types/auth";
import type { ProjectSummary, RuntimeInspectionSnapshot } from "../../../shared/types/project";
import { ProjectDetailPanel } from "./ProjectDetailPanel";

const currentUser: UserSummary = {
  id: 1,
  is_active: true,
  role: "admin",
  username: "runtime-admin",
};

const selectedProject: ProjectSummary = {
  action_mappings: [
    {
      canonical_action: "status",
      configured_by_user_id: 1,
      script_label: "STATUS",
      source: "user_defined",
    },
  ],
  created_by_user_id: 1,
  description: "Primary managed project",
  id: 7,
  lifecycle_configuration_health: "partial",
  lifecycle_function_configurations: [
    {
      canonical_action: "status",
      description: "Report whether the project appears to be running.",
      preferred_script_identifier: "STATUS",
      script_label: "STATUS",
      state: "configured",
    },
    {
      canonical_action: "start",
      description: "Start the project runtime.",
      preferred_script_identifier: "START",
      script_label: null,
      state: "undefined",
    },
    {
      canonical_action: "stop",
      description: "Stop the project runtime.",
      preferred_script_identifier: "STOP",
      script_label: null,
      state: "unconfigured",
    },
    {
      canonical_action: "restart",
      description: "Restart the project runtime.",
      preferred_script_identifier: "RESTART",
      script_label: null,
      state: "undefined",
    },
  ],
  lifecycle_script_path: "E:/Projects/demo/control.bat",
  owner_user_ids: [1],
  project_root_path: "E:/Projects/demo",
  reference_name: "demo-project",
};

const runtimeSnapshot: RuntimeInspectionSnapshot = {
  application_reachable: true,
  application_url: "http://localhost:4010",
  inspected_at: "2026-08-24T13:11:00+00:00",
  known_port: 4010,
  process_snapshots: [
    {
      cpu_seconds: 1.2,
      memory_bytes: 73400320,
      name: "python",
      pid: 4242,
      started_at: "2026-08-24T13:10:00+00:00",
    },
  ],
  project_id: 7,
  status: "running",
  status_reason: "Found 1 process(es) listening on APP_PORT 4010.",
  uptime_seconds: 123,
};

describe("ProjectDetailPanel", () => {
  it("renders runtime information for the selected project", () => {
    render(
      <ProjectDetailPanel
        activeAction={null}
        configurationMessage={null}
        currentUser={currentUser}
        errorMessage={null}
        isLoadingDetail={false}
        isReloadingProject={false}
        isUpdatingLifecycleConfiguration={false}
        lifecycleResult={null}
        onLogout={vi.fn()}
        onRefreshProject={vi.fn()}
        onReloadProject={vi.fn()}
        onRunLifecycleAction={vi.fn()}
        onUpdateLifecycleConfiguration={vi.fn()}
        runtimeSnapshot={runtimeSnapshot}
        selectedProject={selectedProject}
      />,
    );

    expect(screen.getByText("demo-project")).toBeInTheDocument();
    expect(screen.getByText("http://localhost:4010")).toBeInTheDocument();
    expect(screen.getByText("Reachable")).toBeInTheDocument();
    expect(
      screen.getByText("Found 1 process(es) listening on APP_PORT 4010."),
    ).toBeInTheDocument();
    expect(screen.getByText(/python \(PID 4242\)/)).toBeInTheDocument();
    expect(screen.getByText("partial")).toBeInTheDocument();
    const startButton = screen
      .getAllByRole("button")
      .find((button) => button.textContent === "startundefined");
    expect(startButton).toBeDefined();
    expect(startButton).toBeDisabled();
  });

  it("triggers configured lifecycle actions from the operator controls", () => {
    const onRunLifecycleAction = vi.fn();

    render(
      <ProjectDetailPanel
        activeAction={null}
        configurationMessage={null}
        currentUser={currentUser}
        errorMessage={null}
        isLoadingDetail={false}
        isReloadingProject={false}
        isUpdatingLifecycleConfiguration={false}
        lifecycleResult={null}
        onLogout={vi.fn()}
        onRefreshProject={vi.fn()}
        onReloadProject={vi.fn()}
        onRunLifecycleAction={onRunLifecycleAction}
        onUpdateLifecycleConfiguration={vi.fn()}
        runtimeSnapshot={runtimeSnapshot}
        selectedProject={selectedProject}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /status configured/ }));

    expect(onRunLifecycleAction).toHaveBeenCalledWith("status");
  });

  it("submits manual lifecycle configuration from the mapping dialog", () => {
    const onUpdateLifecycleConfiguration = vi.fn();

    render(
      <ProjectDetailPanel
        activeAction={null}
        configurationMessage={null}
        currentUser={currentUser}
        errorMessage={null}
        isLoadingDetail={false}
        isReloadingProject={false}
        isUpdatingLifecycleConfiguration={false}
        lifecycleResult={null}
        onLogout={vi.fn()}
        onRefreshProject={vi.fn()}
        onReloadProject={vi.fn()}
        onRunLifecycleAction={vi.fn()}
        onUpdateLifecycleConfiguration={onUpdateLifecycleConfiguration}
        runtimeSnapshot={runtimeSnapshot}
        selectedProject={selectedProject}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Configure mappings" }));
    fireEvent.change(screen.getAllByLabelText("Script label", { selector: "input" })[0], {
      target: { value: "STATUS" },
    });
    fireEvent.change(screen.getByPlaceholderText("START"), {
      target: { value: "INICIAR" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save configuration" }));

    expect(onUpdateLifecycleConfiguration).toHaveBeenCalledWith({
      mappings: [
        {
          canonical_action: "status",
          script_label: "STATUS",
          source: "user_defined",
        },
        {
          canonical_action: "start",
          script_label: "INICIAR",
          source: "user_defined",
        },
      ],
      unconfigured_actions: ["stop"],
    });
  });
});
