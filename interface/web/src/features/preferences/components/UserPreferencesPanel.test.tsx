import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { UserPreferences } from "../../../shared/types/preferences";
import { UserPreferencesPanel } from "./UserPreferencesPanel";

const preferences: UserPreferences = {
  locale: "pt-BR",
  project_view_mode: "list",
  status_refresh_interval_seconds: 30,
  user_id: 1,
};

function renderUserPreferencesPanel(
  overrides: Partial<Parameters<typeof UserPreferencesPanel>[0]> = {},
) {
  const props: Parameters<typeof UserPreferencesPanel>[0] = {
    errorMessage: null,
    isLoading: false,
    isSaving: false,
    message: null,
    onRefresh: vi.fn(),
    onUpdate: vi.fn(),
    preferences,
    ...overrides,
  };

  render(<UserPreferencesPanel {...props} />);

  return props;
}

describe("UserPreferencesPanel", () => {
  it("renders current authenticated user preferences", () => {
    renderUserPreferencesPanel();

    expect(screen.getByText("User display settings")).toBeInTheDocument();
    expect(screen.getByLabelText("Language")).toHaveValue("pt-BR");
    expect(screen.getByLabelText("List")).toBeChecked();
    expect(screen.getByLabelText("Status refresh interval")).toHaveValue(30);
  });

  it("submits a partial preference update payload through the panel", () => {
    const onUpdate = vi.fn();
    renderUserPreferencesPanel({ onUpdate });

    fireEvent.change(screen.getByLabelText("Language"), {
      target: { value: "en-US" },
    });
    fireEvent.click(screen.getByLabelText("Table"));
    fireEvent.change(screen.getByLabelText("Status refresh interval"), {
      target: { value: "45" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save preferences" }));

    expect(onUpdate).toHaveBeenCalledWith({
      locale: "en-US",
      project_view_mode: "table",
      status_refresh_interval_seconds: 45,
    });
  });

  it("renders preference save feedback and API errors", () => {
    renderUserPreferencesPanel({
      errorMessage: "Unable to save",
      message: "Preferences saved.",
    });

    expect(screen.getByText("Preferences saved.")).toBeInTheDocument();
    expect(screen.getByText("Unable to save")).toBeInTheDocument();
  });
});
