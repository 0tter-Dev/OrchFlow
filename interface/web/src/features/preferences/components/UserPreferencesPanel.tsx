import "./UserPreferencesPanel.css";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useTranslation } from "react-i18next";

import { ErrorNotice } from "../../../shared/components/ErrorNotice";
import type {
  AccentColor,
  AppearanceMode,
  ProjectViewMode,
  UserLocale,
  UserPreferences,
  UserPreferencesUpdate,
} from "../../../shared/types/preferences";
import "../../../app/i18n";

type UserPreferencesPanelProps = {
  errorMessage: string | null;
  isLoading: boolean;
  isSaving: boolean;
  message: string | null;
  onRefresh: () => void;
  onUpdate: (payload: UserPreferencesUpdate) => void;
  preferences: UserPreferences | null;
};

type UserPreferencesFormState = {
  locale: UserLocale;
  project_view_mode: ProjectViewMode;
  appearance_mode: AppearanceMode;
  accent_color: AccentColor;
  status_refresh_interval_seconds: string;
};

const defaultFormState: UserPreferencesFormState = {
  locale: "pt-BR",
  project_view_mode: "list",
  appearance_mode: "gray-dark",
  accent_color: "green",
  status_refresh_interval_seconds: "30",
};

function formStateFromPreferences(
  preferences: UserPreferences | null,
): UserPreferencesFormState {
  if (preferences === null) {
    return defaultFormState;
  }

  return {
    locale: preferences.locale,
    project_view_mode: preferences.project_view_mode,
    appearance_mode: preferences.appearance_mode,
    accent_color: preferences.accent_color,
    status_refresh_interval_seconds: String(preferences.status_refresh_interval_seconds),
  };
}

export function UserPreferencesPanel({
  errorMessage,
  isLoading,
  isSaving,
  message,
  onRefresh,
  onUpdate,
  preferences,
}: UserPreferencesPanelProps) {
  const { t } = useTranslation();
  const [formState, setFormState] = useState<UserPreferencesFormState>(
    formStateFromPreferences(preferences),
  );

  useEffect(() => {
    setFormState(formStateFromPreferences(preferences));
  }, [preferences]);

  function updateField<Field extends keyof UserPreferencesFormState>(
    field: Field,
    value: UserPreferencesFormState[Field],
  ) {
    setFormState((currentState) => ({
      ...currentState,
      [field]: value,
    }));
  }

  function submitPreferences(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onUpdate({
      locale: formState.locale,
      project_view_mode: formState.project_view_mode,
      appearance_mode: formState.appearance_mode,
      accent_color: formState.accent_color,
      status_refresh_interval_seconds: Number(formState.status_refresh_interval_seconds),
    });
  }

  return (
    <section className="preferences-panel">
      <header className="preferences-panel__header">
        <div>
          <span className="preferences-panel__eyebrow">{t("workspace.preferencesWorkspace")}</span>
          <h2 className="preferences-panel__title">{t("workspace.preferencesTitle")}</h2>
        </div>
        <button className="preferences-panel__button" onClick={onRefresh} type="button">
          {t("workspace.preferencesRefresh")}
        </button>
      </header>

      {errorMessage !== null ? (
        <ErrorNotice
          className="preferences-panel__notice"
          message={errorMessage}
          title={t("workspace.preferencesError")}
        />
      ) : null}
      {message !== null ? <div className="preferences-panel__success">{message}</div> : null}

      <form className="preferences-panel__form" onSubmit={submitPreferences}>
        <label className="preferences-panel__field">
          <span>{t("workspace.preferencesLanguage")}</span>
          <select
            disabled={isLoading || isSaving}
            onChange={(event) => updateField("locale", event.target.value as UserLocale)}
            value={formState.locale}
          >
            <option value="pt-BR">{t("workspace.preferencesPortuguese")}</option>
            <option value="en-US">{t("workspace.preferencesEnglish")}</option>
          </select>
        </label>

        <label className="preferences-panel__field">
          <span>{t("workspace.preferencesAppearance")}</span>
          <select
            disabled={isLoading || isSaving}
            onChange={(event) => updateField("appearance_mode", event.target.value as AppearanceMode)}
            value={formState.appearance_mode}
          >
            <option value="cream-light">{t("workspace.preferencesAppearanceCream")}</option>
            <option value="white-high-contrast">{t("workspace.preferencesAppearanceWhite")}</option>
            <option value="gray-dark">{t("workspace.preferencesAppearanceGray")}</option>
            <option value="black-high-contrast">{t("workspace.preferencesAppearanceBlack")}</option>
          </select>
        </label>

        <label className="preferences-panel__field">
          <span>{t("workspace.preferencesAccent")}</span>
          <select
            disabled={isLoading || isSaving}
            onChange={(event) => updateField("accent_color", event.target.value as AccentColor)}
            value={formState.accent_color}
          >
            <option value="blue">{t("workspace.preferencesAccentBlue")}</option>
            <option value="green">{t("workspace.preferencesAccentGreen")}</option>
            <option value="red">{t("workspace.preferencesAccentRed")}</option>
            <option value="yellow">{t("workspace.preferencesAccentYellow")}</option>
            <option value="orange">{t("workspace.preferencesAccentOrange")}</option>
            <option value="purple">{t("workspace.preferencesAccentPurple")}</option>
            <option value="pink">{t("workspace.preferencesAccentPink")}</option>
          </select>
        </label>

        <fieldset className="preferences-panel__mode">
          <legend>{t("workspace.preferencesProjectDisplay")}</legend>
          <label>
            <input
              checked={formState.project_view_mode === "list"}
              disabled={isLoading || isSaving}
              name="project-view-mode"
              onChange={() => updateField("project_view_mode", "list")}
              type="radio"
            />
            <span>{t("workspace.preferencesList")}</span>
          </label>
          <label>
            <input
              checked={formState.project_view_mode === "table"}
              disabled={isLoading || isSaving}
              name="project-view-mode"
              onChange={() => updateField("project_view_mode", "table")}
              type="radio"
            />
            <span>{t("workspace.preferencesTable")}</span>
          </label>
        </fieldset>

        <label className="preferences-panel__field">
          <span>{t("workspace.preferencesStatusRefreshInterval")}</span>
          <input
            disabled={isLoading || isSaving}
            max={300}
            min={10}
            onChange={(event) =>
              updateField("status_refresh_interval_seconds", event.target.value)
            }
            type="number"
            value={formState.status_refresh_interval_seconds}
          />
        </label>

        <button className="preferences-panel__submit" disabled={isLoading || isSaving} type="submit">
          {isSaving ? t("workspace.preferencesSaving") : t("workspace.preferencesSave")}
        </button>
      </form>
    </section>
  );
}
