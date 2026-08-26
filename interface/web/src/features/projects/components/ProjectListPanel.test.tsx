import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { UserSummary } from "../../../shared/types/auth";
import { ProjectListPanel } from "./ProjectListPanel";

const currentUser: UserSummary = {
  id: 1,
  is_active: true,
  role: "admin",
  username: "operator-admin",
};

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
});
