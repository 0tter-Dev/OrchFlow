import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import i18n from "../../../app/i18n";
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
  beforeEach(async () => {
    await i18n.changeLanguage("pt-BR");
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders current authenticated user preferences", () => {
    renderUserPreferencesPanel();

    expect(screen.getByText("Configurações de exibição")).toBeInTheDocument();
    expect(screen.getByLabelText("Idioma")).toHaveValue("pt-BR");
    expect(screen.getByLabelText("Lista")).toBeChecked();
    expect(screen.getByLabelText("Intervalo de atualização de status")).toHaveValue(30);
  });

  it("submits a partial preference update payload through the panel", () => {
    const onUpdate = vi.fn();
    renderUserPreferencesPanel({ onUpdate });

    fireEvent.change(screen.getByLabelText("Idioma"), {
      target: { value: "en-US" },
    });
    fireEvent.click(screen.getByLabelText("Tabela"));
    fireEvent.change(screen.getByLabelText("Intervalo de atualização de status"), {
      target: { value: "45" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Salvar preferências" }));

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

  it("renders translated preference controls when the persisted locale is English", async () => {
    await i18n.changeLanguage("en-US");
    renderUserPreferencesPanel({
      preferences: { ...preferences, locale: "en-US" },
    });

    expect(screen.getByText("User display settings")).toBeInTheDocument();
    expect(screen.getByLabelText("Language")).toHaveValue("en-US");
    expect(screen.getByRole("button", { name: "Save preferences" })).toBeInTheDocument();
  });
});
