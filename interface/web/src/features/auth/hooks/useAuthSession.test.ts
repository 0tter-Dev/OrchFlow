import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { getCurrentUser, loginUser, registerUser } from "../../../shared/api/auth";
import { useAuthSession } from "./useAuthSession";

vi.mock("../../../shared/api/auth", () => ({
  getCurrentUser: vi.fn(),
  loginUser: vi.fn(),
  registerUser: vi.fn(),
}));

const currentUser = {
  id: 1,
  is_active: true,
  role: "admin" as const,
  username: "first-admin",
};

const accessToken = {
  access_token: "signed-token",
  expires_in_seconds: 3600,
  token_type: "bearer",
};

describe("useAuthSession", () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  it("creates an account and signs in with the new credentials", async () => {
    vi.mocked(registerUser).mockResolvedValue(currentUser);
    vi.mocked(loginUser).mockResolvedValue(accessToken);
    vi.mocked(getCurrentUser).mockResolvedValue(currentUser);

    const { result } = renderHook(() => useAuthSession());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.createAccount("first-admin", "password123");
    });

    expect(registerUser).toHaveBeenCalledWith({
      password: "password123",
      username: "first-admin",
    });
    expect(loginUser).toHaveBeenCalledWith({
      password: "password123",
      username: "first-admin",
    });
    expect(getCurrentUser).toHaveBeenCalledWith("signed-token");
    expect(window.localStorage.getItem("orchflow.auth.token")).toBe("signed-token");
    expect(result.current.currentUser).toEqual(currentUser);
    expect(result.current.token).toBe("signed-token");
    expect(result.current.errorMessage).toBeNull();
  });

  it("signs in and hydrates the authenticated user", async () => {
    vi.mocked(loginUser).mockResolvedValue(accessToken);
    vi.mocked(getCurrentUser).mockResolvedValue(currentUser);

    const { result } = renderHook(() => useAuthSession());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    await act(async () => {
      await result.current.login("first-admin", "password123");
    });

    expect(loginUser).toHaveBeenCalledWith({
      password: "password123",
      username: "first-admin",
    });
    expect(result.current.currentUser).toEqual(currentUser);
    expect(result.current.token).toBe("signed-token");
    expect(result.current.statusMessage).toBeNull();
  });

  it("surfaces login failures without storing a token", async () => {
    vi.mocked(loginUser).mockRejectedValue(new Error("Invalid credentials."));

    const { result } = renderHook(() => useAuthSession());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    window.localStorage.setItem("orchflow.auth.token", "stale-token");

    await act(async () => {
      await result.current.login("first-admin", "wrong-password");
    });

    expect(window.localStorage.getItem("orchflow.auth.token")).toBeNull();
    expect(result.current.currentUser).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.errorMessage).toBe("Unable to sign in. Invalid credentials.");
  });
});
