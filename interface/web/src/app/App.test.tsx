import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { workspaceNavigationItems } from "./workspace-navigation";

vi.mock("../features/auth/hooks/useAuthSession", () => ({
  useAuthSession: () => ({
    createAccount: vi.fn(),
    currentUser: null,
    errorMessage: null,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    statusMessage: null,
    token: null,
  }),
}));

describe("App unauthenticated shell", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the focused authentication surface without workspace chrome", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "OrchFlow" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Login" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Create account" })).toBeInTheDocument();
    expect(screen.queryByText("System probe")).not.toBeInTheDocument();
    expect(screen.queryByText("API health:")).not.toBeInTheDocument();
  });
});

describe("workspace navigation", () => {
  const copy = {
    activity: "Activity",
    admin: "Admin",
    ai: "AI assistance",
    overview: "Overview",
    profile: "Profile",
    projects: "Projects",
    settings: "Settings",
  };

  it("keeps administrative navigation unavailable to members", () => {
    expect(workspaceNavigationItems("member", copy).map((item) => item.to)).toEqual([
      "/overview",
      "/projects",
      "/ai",
      "/activity",
      "/settings",
      "/profile",
    ]);
  });

  it("adds the administrative route for administrators", () => {
    expect(workspaceNavigationItems("admin", copy).at(-1)).toEqual({
      label: "Admin",
      to: "/admin",
    });
  });
});
