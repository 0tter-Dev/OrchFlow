import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LoginPanel } from "./LoginPanel";

describe("LoginPanel", () => {
  it("submits the entered credentials", () => {
    const onSubmit = vi.fn();

    render(<LoginPanel errorMessage={null} isLoading={false} onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("Username"), {
      target: { value: "runtime-admin" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Open operator session" }));

    expect(onSubmit).toHaveBeenCalledWith("runtime-admin", "password123");
  });

  it("renders an error message when login fails", () => {
    render(
      <LoginPanel
        errorMessage="Invalid credentials."
        isLoading={false}
        onSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText("Invalid credentials.")).toBeInTheDocument();
  });
});
