import { Link } from "react-router";

import type { AuditEventSummary } from "../../../shared/types/audit";

type ProjectOperationalHistoryProps = {
  canLoadAuditEvents: boolean;
  events: AuditEventSummary[];
  projectId: number;
};

function outcome(event: AuditEventSummary): string {
  if (event.details?.includes("succeeded:true")) return "Succeeded";
  if (event.details?.includes("succeeded:false")) return "Failed";
  if (event.action.includes("reject") || event.action.includes("blocked")) return "Rejected";
  return "Recorded";
}

export function ProjectOperationalHistory({
  canLoadAuditEvents,
  events,
  projectId,
}: ProjectOperationalHistoryProps) {
  if (!canLoadAuditEvents) {
    return <section className="project-detail__history"><h3>Recent operational history</h3><p>Operational history remains available through the administrator Activity workspace.</p></section>;
  }

  const projectEvents = events
    .filter((event) => event.target_id === String(projectId))
    .slice(0, 3);

  return (
    <section className="project-detail__history">
      <div className="project-list__title-row"><h3 className="project-list__title">Recent operational history</h3><Link to="/activity">Open full history</Link></div>
      {projectEvents.length === 0 ? <p>No authorized operational events are available for this project yet.</p> : <div className="project-detail__mappings">{projectEvents.map((event) => <article className="project-detail__mapping" key={event.id}><strong>{event.action}</strong><span>{outcome(event)} · {new Date(event.created_at).toLocaleString()}</span></article>)}</div>}
    </section>
  );
}
