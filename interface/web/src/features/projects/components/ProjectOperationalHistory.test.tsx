import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router";
import { describe, expect, it } from "vitest";

import { ProjectOperationalHistory } from "./ProjectOperationalHistory";

describe("ProjectOperationalHistory", () => {
  it("shows only the selected project's recent authorized outcomes", () => {
    render(<BrowserRouter><ProjectOperationalHistory canLoadAuditEvents events={[{ action: "lifecycle.start", actor_user_id: 1, created_at: "2026-09-20T00:00:00Z", details: "succeeded:true", id: 1, target_id: "7", target_type: "project" }, { action: "lifecycle.stop", actor_user_id: 1, created_at: "2026-09-20T00:00:00Z", details: "succeeded:false", id: 2, target_id: "8", target_type: "project" }]} projectId={7} /></BrowserRouter>);

    expect(screen.getByText("lifecycle.start")).toBeInTheDocument();
    expect(screen.getByText("Succeeded", { exact: false })).toBeInTheDocument();
    expect(screen.queryByText("lifecycle.stop")).not.toBeInTheDocument();
  });

  it("does not expose history to users without audit authorization", () => {
    render(<BrowserRouter><ProjectOperationalHistory canLoadAuditEvents={false} events={[]} projectId={7} /></BrowserRouter>);

    expect(screen.getByText(/administrator Activity workspace/)).toBeInTheDocument();
  });
});
