import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import i18n from "../../../app/i18n";
import type { SystemHealthSnapshot } from "../../../shared/types/system";
import { HealthCheckCard } from "./HealthCheckCard";

const snapshot: SystemHealthSnapshot = {
  name: "OrchFlow",
  stage: "bootstrap",
  status: "ok",
  version: "0.2.9",
};

describe("HealthCheckCard", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("en-US");
  });

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
    expect(screen.getByText("0.2.9")).toBeInTheDocument();
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

  it("keeps the latest health snapshot visible while refreshing", () => {
    render(
      <HealthCheckCard
        apiBaseUrl="http://localhost:8000"
        errorMessage={null}
        healthStatus={snapshot}
        isLoading={true}
        lastUpdated={new Date("2026-08-24T12:00:00Z")}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Refreshing latest API status...")).toBeInTheDocument();
    expect(screen.getByText("ok")).toBeInTheDocument();
    expect(screen.getByText("bootstrap")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Saving..." })).toBeInTheDocument();
  });

  it("keeps the latest health snapshot visible with a refresh error", () => {
    render(
      <HealthCheckCard
        apiBaseUrl="http://localhost:8000"
        errorMessage="Transient network failure"
        healthStatus={snapshot}
        isLoading={false}
        lastUpdated={new Date("2026-08-24T12:00:00Z")}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Transient network failure")).toBeInTheDocument();
    expect(screen.getByText("ok")).toBeInTheDocument();
    expect(screen.getByText("0.2.9")).toBeInTheDocument();
  });

  it("uses Portuguese labels when the saved locale is Portuguese", async () => {
    await i18n.changeLanguage("pt-BR");
    render(<HealthCheckCard apiBaseUrl="http://localhost:8000" errorMessage={null} healthStatus={snapshot} isLoading={false} lastUpdated={null} onRefresh={vi.fn()} />);
    expect(screen.getByText("Status do backend")).toBeInTheDocument();
    expect(screen.getByText("Destino")).toBeInTheDocument();
  });
});
