import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import "../../../app/i18n";

import type { AuditEventSummary } from "../../../shared/types/audit";

type ProjectOperationalHistoryProps = {
  canLoadAuditEvents: boolean;
  events: AuditEventSummary[];
  projectId: number;
};

export function ProjectOperationalHistory({
  canLoadAuditEvents,
  events,
  projectId,
}: ProjectOperationalHistoryProps) {
  const { i18n, t } = useTranslation();
  const outcome = (event: AuditEventSummary): string => {
    if (event.details?.includes("succeeded:true")) return t("workspace.succeeded");
    if (event.details?.includes("succeeded:false")) return t("workspace.failed");
    if (event.action.includes("reject") || event.action.includes("blocked")) return t("workspace.rejected");
    return t("workspace.recorded");
  };
  if (!canLoadAuditEvents) {
    return <section className="project-detail__history"><h3>{t("workspace.recentHistory")}</h3><p>{t("workspace.historyAdminOnly")}</p></section>;
  }

  const projectEvents = events
    .filter(
      (event) => event.target_type === "project" && event.target_id === String(projectId),
    )
    .slice(0, 3);

  return (
    <section className="project-detail__history">
      <div className="project-list__title-row"><h3 className="project-list__title">{t("workspace.recentHistory")}</h3><Link to={`/activity?project_id=${projectId}`}>{t("workspace.openFullHistory")}</Link></div>
      {projectEvents.length === 0 ? <p>{t("workspace.noProjectEvents")}</p> : <div className="project-detail__mappings">{projectEvents.map((event) => <article className="project-detail__mapping" key={event.id}><strong>{event.action}</strong><span>{outcome(event)} · {new Date(event.created_at).toLocaleString(i18n.language)}</span></article>)}</div>}
    </section>
  );
}
