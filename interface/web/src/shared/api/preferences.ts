import { requestJson } from "./client";
import type { UserPreferences, UserPreferencesUpdate } from "../types/preferences";

export function getUserPreferences(token: string): Promise<UserPreferences> {
  return requestJson<UserPreferences>("/auth/me/preferences", { token });
}

export function updateUserPreferences(
  token: string,
  payload: UserPreferencesUpdate,
): Promise<UserPreferences> {
  return requestJson<UserPreferences>("/auth/me/preferences", {
    body: payload,
    method: "PATCH",
    token,
  });
}
