import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { SystemHealthSnapshot } from "../../../shared/types/system";
import { HealthCheckCard } from "./HealthCheckCard";

const snapshot: SystemHealthSnapshot = {
  name: "OrchFlow",
  stage: "bootstrap",
  status: "ok",
  version: "0.2.0",
};

describe("HealthCheckCard", () => {
  it("renders the successful backend health response", () => {
    render(
      <HealthCheckCard
        apiBaseUrl="http://localhost:8000"
        errorMessage={null}
        healthStatus={snapshot}
        isLoading={false}
        lastUpdated={new Date("2026-08-24T12:00:00Z")}
        onRefresh={vi.fn()}
      />
    );

    expect(screen.getByText("Backend status")).toBeInTheDocument();
    expect(screen.getByText("ok")).toBeInTheDocument();
    expect(screen.getByText("bootstrap")).toBeInTheDocument();
    expect(screen.getByText("0.2.0")).toBeInTheDocument();
  });

  it("renders an error state when the API is unavailable", () => {
    render(
      <HealthCheckCard
        apiBaseUrl="http://localhost:8000"
        errorMessage="API unavailable"
        healthStatus={null}
        isLoading={false}
        lastUpdated={null}
        onRefresh={vi.fn()}
      />
    );

    expect(screen.getByText("Unable to reach the OrchFlow API.")).toBeInTheDocument();
    expect(screen.getByText("API unavailable")).toBeInTheDocument();
  });
});
