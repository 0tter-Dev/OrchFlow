export type UserLocale = "pt-BR" | "en-US";

export type ProjectViewMode = "list" | "table";
export type AppearanceMode = "cream-light" | "white-high-contrast" | "gray-dark" | "black-high-contrast";
export type AccentColor = "blue" | "green" | "red" | "yellow" | "orange" | "purple" | "pink";

export type UserPreferences = {
  user_id: number;
  locale: UserLocale;
  project_view_mode: ProjectViewMode;
  appearance_mode: AppearanceMode;
  accent_color: AccentColor;
  status_refresh_interval_seconds: number;
};

export type UserPreferencesUpdate = {
  locale?: UserLocale;
  project_view_mode?: ProjectViewMode;
  appearance_mode?: AppearanceMode;
  accent_color?: AccentColor;
  status_refresh_interval_seconds?: number;
};
