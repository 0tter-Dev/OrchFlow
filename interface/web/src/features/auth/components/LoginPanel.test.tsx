import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LoginPanel } from "./LoginPanel";

describe("LoginPanel", () => {
  it("submits the entered credentials", () => {
    const onSubmit = vi.fn();

    render(
      <LoginPanel
        errorMessage={null}
        isLoading={false}
        onCreateAccount={vi.fn()}
        onSubmit={onSubmit}
        statusMessage={null}
      />,
    );

    fireEvent.change(screen.getByLabelText("Username"), {
      target: { value: "runtime-admin" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Login" }));

    expect(onSubmit).toHaveBeenCalledWith("runtime-admin", "password123");
  });

  it("submits role-neutral account creation from the create account mode", () => {
    const onCreateAccount = vi.fn();

    render(
      <LoginPanel
        errorMessage={null}
        isLoading={false}
        onCreateAccount={onCreateAccount}
        onSubmit={vi.fn()}
        statusMessage={null}
      />,
    );

    fireEvent.click(screen.getByRole("tab", { name: "Create account" }));
    fireEvent.change(screen.getByLabelText("Username"), {
      target: { value: "first-admin" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));

    expect(onCreateAccount).toHaveBeenCalledWith("first-admin", "password123");
  });

  it("renders an error message when login fails", () => {
    render(
      <LoginPanel
        errorMessage="Invalid credentials."
        isLoading={false}
        onCreateAccount={vi.fn()}
        onSubmit={vi.fn()}
        statusMessage={null}
      />,
    );

    expect(screen.getByText("Invalid credentials.")).toBeInTheDocument();
  });

  it("shows session progress feedback while the request is running", () => {
    render(
      <LoginPanel
        errorMessage={null}
        isLoading={true}
        onCreateAccount={vi.fn()}
        onSubmit={vi.fn()}
        statusMessage="Account created. Signing in..."
      />,
    );

    expect(screen.getByRole("status")).toHaveTextContent("Account created. Signing in...");
    expect(
      screen.getByRole("button", { name: "Account created. Signing in..." }),
    ).toBeDisabled();
  });

  it("toggles password visibility", () => {
    render(
      <LoginPanel
        errorMessage={null}
        isLoading={false}
        onCreateAccount={vi.fn()}
        onSubmit={vi.fn()}
        statusMessage={null}
      />,
    );

    const passwordInput = screen.getByLabelText("Password");

    expect(passwordInput).toHaveAttribute("type", "password");

    fireEvent.click(screen.getByRole("button", { name: "Show password" }));

    expect(passwordInput).toHaveAttribute("type", "text");

    fireEvent.click(screen.getByRole("button", { name: "Hide password" }));

    expect(passwordInput).toHaveAttribute("type", "password");
  });
});
