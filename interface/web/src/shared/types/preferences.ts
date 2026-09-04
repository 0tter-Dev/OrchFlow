export type UserLocale = "pt-BR" | "en-US";

export type ProjectViewMode = "list" | "table";

export type UserPreferences = {
  user_id: number;
  locale: UserLocale;
  project_view_mode: ProjectViewMode;
  status_refresh_interval_seconds: number;
};

export type UserPreferencesUpdate = {
  locale?: UserLocale;
  project_view_mode?: ProjectViewMode;
  status_refresh_interval_seconds?: number;
};
