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
  lifecycle_script_path: "E:/Projects/demo/control.bat",
  owner_user_ids: [1],
  project_root_path: "E:/Projects/demo",
  reference_name: "demo-project",
};

const runtimeSnapshot: RuntimeInspectionSnapshot = {
  application_url: "http://localhost:4010",
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
  uptime_seconds: 123,
};

describe("ProjectDetailPanel", () => {
  it("renders runtime information for the selected project", () => {
    render(
      <ProjectDetailPanel
        activeAction={null}
        currentUser={currentUser}
        errorMessage={null}
        isLoadingDetail={false}
        lifecycleResult={null}
        onLogout={vi.fn()}
        onRefreshProject={vi.fn()}
        onRunLifecycleAction={vi.fn()}
        runtimeSnapshot={runtimeSnapshot}
        selectedProject={selectedProject}
      />,
    );

    expect(screen.getByText("demo-project")).toBeInTheDocument();
    expect(screen.getByText("http://localhost:4010")).toBeInTheDocument();
    expect(screen.getByText(/python \(PID 4242\)/)).toBeInTheDocument();
  });

  it("triggers lifecycle actions from the operator controls", () => {
    const onRunLifecycleAction = vi.fn();

    render(
      <ProjectDetailPanel
        activeAction={null}
        currentUser={currentUser}
        errorMessage={null}
        isLoadingDetail={false}
        lifecycleResult={null}
        onLogout={vi.fn()}
        onRefreshProject={vi.fn()}
        onRunLifecycleAction={onRunLifecycleAction}
        runtimeSnapshot={runtimeSnapshot}
        selectedProject={selectedProject}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "start" }));

    expect(onRunLifecycleAction).toHaveBeenCalledWith("start");
  });
});
