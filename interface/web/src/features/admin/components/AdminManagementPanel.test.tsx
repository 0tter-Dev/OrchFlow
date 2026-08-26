import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { UserSummary } from "../../../shared/types/auth";
import type { ProjectSummary } from "../../../shared/types/project";
import { AdminManagementPanel } from "./AdminManagementPanel";

const currentUser: UserSummary = {
  id: 1,
  is_active: true,
  role: "admin",
  username: "admin-user",
};

const memberUser: UserSummary = {
  id: 2,
  is_active: true,
  role: "member",
  username: "member-user",
};

const selectedProject: ProjectSummary = {
  action_mappings: [],
  created_by_user_id: 1,
  description: "Managed project",
  id: 7,
  lifecycle_script_path: "E:/Projects/demo/control.bat",
  owner_user_ids: [1],
  project_root_path: "E:/Projects/demo",
  reference_name: "demo-project",
};

function renderPanel(overrides: Partial<Parameters<typeof AdminManagementPanel>[0]> = {}) {
  const props: Parameters<typeof AdminManagementPanel>[0] = {
    canManage: true,
    currentUser,
    errorMessage: null,
    isLoading: false,
    isMutating: false,
    onAddOwner: vi.fn(),
    onChangeUserActivation: vi.fn(),
    onChangeUserRole: vi.fn(),
    onRefreshProject: vi.fn(),
    onRefreshUsers: vi.fn(),
    onRemoveOwner: vi.fn(),
    selectedProject,
    successMessage: null,
    users: [currentUser, memberUser],
    ...overrides,
  };

  render(<AdminManagementPanel {...props} />);

  return props;
}

describe("AdminManagementPanel", () => {
  it("updates user roles from the user controls", () => {
    const onChangeUserRole = vi.fn();
    renderPanel({ onChangeUserRole });

    fireEvent.change(screen.getByLabelText("Role for member-user"), {
      target: { value: "admin" },
    });

    expect(onChangeUserRole).toHaveBeenCalledWith(2, "admin");
  });

  it("adds selected project owners from active users", () => {
    const onAddOwner = vi.fn();
    const onRefreshProject = vi.fn();
    renderPanel({ onAddOwner, onRefreshProject });

    fireEvent.click(screen.getByRole("button", { name: "Add member-user" }));

    expect(onAddOwner).toHaveBeenCalledWith(selectedProject, 2, onRefreshProject);
  });
});
