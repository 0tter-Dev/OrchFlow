import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { UserSummary } from "../../../shared/types/auth";
import type { ProjectSummary } from "../../../shared/types/project";
import { ProjectListPanel } from "./ProjectListPanel";

const currentUser: UserSummary = {
  id: 1,
  is_active: true,
  role: "admin",
  username: "operator-admin",
};

const managedProjects: ProjectSummary[] = [
  {
    action_mappings: [],
    created_by_user_id: 1,
    description: "Local API controlled by an existing script",
    id: 7,
    lifecycle_configuration_health: "partial",
    lifecycle_function_configurations: [],
    lifecycle_script_path: "E:\\Projects\\local-api\\control.bat",
    owner_user_ids: [1, 2],
    project_root_path: "E:\\Projects\\local-api",
    reference_name: "local-api",
  },
];

function renderProjectListPanel(
  overrides: Partial<Parameters<typeof ProjectListPanel>[0]> = {},
) {
  const props: Parameters<typeof ProjectListPanel>[0] = {
    currentUser,
    errorMessage: null,
    isLoading: false,
    isRegisteringProject: false,
    onRefresh: vi.fn(),
    onRegisterProject: vi.fn(),
    onSearchQueryChange: vi.fn(),
    onSelectProject: vi.fn(),
    projects: [],
    registrationMessage: null,
    searchQuery: "",
    selectedProjectId: null,
    ...overrides,
  };

  render(<ProjectListPanel {...props} />);

  return props;
}

describe("ProjectListPanel", () => {
  it("submits a project registration with optional lifecycle mappings", () => {
    const onRegisterProject = vi.fn();
    renderProjectListPanel({ onRegisterProject });

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "local-api" },
    });
    fireEvent.change(screen.getByLabelText("Description"), {
      target: { value: "Local API controlled by an existing script" },
    });
    fireEvent.change(screen.getByLabelText("Project root path"), {
      target: { value: "E:\\Projects\\local-api" },
    });
    fireEvent.change(screen.getByLabelText("Lifecycle script path"), {
      target: { value: "E:\\Projects\\local-api\\control.bat" },
    });
    fireEvent.change(screen.getByLabelText("Start mapping"), {
      target: { value: "INICIAR" },
    });
    fireEvent.change(screen.getByLabelText("Stop mapping"), {
      target: { value: "PARAR" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Register" }));

    expect(onRegisterProject).toHaveBeenCalledWith({
      description: "Local API controlled by an existing script",
      lifecycle_script_path: "E:\\Projects\\local-api\\control.bat",
      mappings: [
        {
          canonical_action: "start",
          script_label: "INICIAR",
          source: "user_defined",
        },
        {
          canonical_action: "stop",
          script_label: "PARAR",
          source: "user_defined",
        },
      ],
      project_root_path: "E:\\Projects\\local-api",
      reference_name: "local-api",
    });
  });

  it("renders the registration success message", () => {
    renderProjectListPanel({
      registrationMessage: "local-api registered successfully.",
    });

    expect(screen.getByText("local-api registered successfully.")).toBeInTheDocument();
  });

  it("selects a visible registered project from the operator list", () => {
    const onSelectProject = vi.fn();
    renderProjectListPanel({
      onSelectProject,
      projects: managedProjects,
      selectedProjectId: 7,
    });

    expect(screen.getByText("1 project(s) visible")).toBeInTheDocument();
    expect(screen.getByText("partial")).toBeInTheDocument();
    expect(screen.getByText("Local API controlled by an existing script")).toBeInTheDocument();
    expect(screen.getByText("Owners: 1, 2")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /local-api/ }));

    expect(onSelectProject).toHaveBeenCalledWith(7);
  });
});
