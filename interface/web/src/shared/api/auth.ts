import { requestJson } from "./client";
import type { AccessTokenPayload, UserRole, UserSummary } from "../types/auth";

type LoginPayload = {
  password: string;
  username: string;
};

export function loginUser(payload: LoginPayload): Promise<AccessTokenPayload> {
  return requestJson<AccessTokenPayload>("/auth/login", {
    body: payload,
    method: "POST",
  });
}

export function getCurrentUser(token: string): Promise<UserSummary> {
  return requestJson<UserSummary>("/auth/me", { token });
}

export function listUsers(token: string): Promise<UserSummary[]> {
  return requestJson<UserSummary[]>("/auth/users", { token });
}

export function updateUser(
  token: string,
  userId: number,
  payload: { is_active?: boolean; role?: UserRole },
): Promise<UserSummary> {
  return requestJson<UserSummary>(`/auth/users/${userId}`, {
    body: payload,
    method: "PATCH",
    token,
  });
}
