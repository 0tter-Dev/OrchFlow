import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Tooltip } from "./Tooltip";

describe("Tooltip", () => {
  it("shows tooltip content when the trigger receives focus", async () => {
    render(
      <Tooltip content="Refresh the current API health snapshot">
        <button type="button">Refresh</button>
      </Tooltip>,
    );

    fireEvent.focus(screen.getByRole("button", { name: "Refresh" }));

    await waitFor(() => {
      expect(screen.getByRole("tooltip")).toHaveTextContent(
        "Refresh the current API health snapshot",
      );
    });
  });
});
