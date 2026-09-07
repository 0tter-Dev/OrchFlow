import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

vi.mock("../features/auth/hooks/useAuthSession", () => ({
  useAuthSession: () => ({
    createAccount: vi.fn(),
    currentUser: null,
    errorMessage: null,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
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
