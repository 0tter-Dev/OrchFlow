import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { AuditEventSummary } from "../../../shared/types/audit";
import { AuditEventsPanel } from "./AuditEventsPanel";

const auditEvents: AuditEventSummary[] = [
  {
    action: "lifecycle.start",
    actor_user_id: 1,
    created_at: "2026-08-26T01:20:00+00:00",
    details: "identifier:START;exit_code:0;succeeded:true",
    id: 10,
    target_id: "7",
    target_type: "project",
  },
];

const filters = {
  action: "",
  actorUserId: "",
  createdFrom: "",
  createdTo: "",
  limit: "25",
  projectId: "",
};

describe("AuditEventsPanel", () => {
  it("renders recent audit events", () => {
    render(
      <AuditEventsPanel
        canLoadAuditEvents
        errorMessage={null}
        events={auditEvents}
        filters={filters}
        isLoading={false}
        onRefresh={vi.fn()}
        onUpdateFilters={vi.fn()}
      />,
    );

    expect(screen.getByText("lifecycle.start")).toBeInTheDocument();
    expect(screen.getByText("identifier:START;exit_code:0;succeeded:true")).toBeInTheDocument();
    expect(screen.getByText(/actor: 1/)).toBeInTheDocument();
  });

  it("disables refresh when audit history is not available to the user", () => {
    const onRefresh = vi.fn();
    render(
      <AuditEventsPanel
        canLoadAuditEvents={false}
        errorMessage={null}
        events={[]}
        filters={filters}
        isLoading={false}
        onRefresh={onRefresh}
        onUpdateFilters={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Refresh" }));

    expect(screen.getByText("Admin role is required to view audit history.")).toBeInTheDocument();
    expect(onRefresh).not.toHaveBeenCalled();
  });

  it("updates audit filters from compact controls", () => {
    const onUpdateFilters = vi.fn();
    render(
      <AuditEventsPanel
        canLoadAuditEvents
        errorMessage={null}
        events={[]}
        filters={filters}
        isLoading={false}
        onRefresh={vi.fn()}
        onUpdateFilters={onUpdateFilters}
      />,
    );

    fireEvent.change(screen.getByLabelText("Action"), {
      target: { value: "project.register" },
    });

    expect(onUpdateFilters).toHaveBeenCalled();
  });
});
