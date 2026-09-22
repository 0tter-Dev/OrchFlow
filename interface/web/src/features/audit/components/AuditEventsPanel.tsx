import "./AuditEventsPanel.css";

import type { Dispatch, SetStateAction } from "react";
import { useTranslation } from "react-i18next";
import "../../../app/i18n";

import { ErrorNotice } from "../../../shared/components/ErrorNotice";
import type { AuditEventFilters, AuditEventSummary } from "../../../shared/types/audit";

type AuditEventsPanelProps = {
  canLoadAuditEvents: boolean;
  errorMessage: string | null;
  events: AuditEventSummary[];
  filters: AuditEventFilters;
  isLoading: boolean;
  onRefresh: () => void;
  onUpdateFilters: Dispatch<SetStateAction<AuditEventFilters>>;
};

function formatTimestamp(value: string, locale: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(locale);
}

export function AuditEventsPanel({
  canLoadAuditEvents,
  errorMessage,
  events,
  filters,
  isLoading,
  onRefresh,
  onUpdateFilters,
}: AuditEventsPanelProps) {
  const { i18n, t } = useTranslation();
  const updateFilter = (name: keyof AuditEventFilters, value: string) => {
    onUpdateFilters((currentFilters) => ({ ...currentFilters, [name]: value }));
  };

  return (
    <section className="audit-panel">
      <header className="audit-panel__header">
        <div>
          <span className="audit-panel__eyebrow">{t("workspace.auditHistory")}</span>
          <h2 className="audit-panel__title">{t("workspace.recentOperationalEvents")}</h2>
        </div>
        <button
          className="audit-panel__button"
          disabled={!canLoadAuditEvents || isLoading}
          onClick={onRefresh}
          type="button"
        >
          {isLoading ? t("workspace.loading") : t("workspace.refresh")}
        </button>
      </header>

      {!canLoadAuditEvents ? (
        <div className="audit-panel__empty">{t("workspace.adminRequiredAudit")}</div>
      ) : null}

      {canLoadAuditEvents ? (
        <div className="audit-panel__filters">
          <label className="audit-panel__field">
            <span>{t("workspace.limit")}</span>
            <input
              min="1"
              max="100"
              onChange={(event) => updateFilter("limit", event.target.value)}
              type="number"
              value={filters.limit}
            />
          </label>
          <label className="audit-panel__field">
            <span>{t("workspace.action")}</span>
            <input
              onChange={(event) => updateFilter("action", event.target.value)}
              placeholder="project.register"
              value={filters.action}
            />
          </label>
          <label className="audit-panel__field">
            <span>{t("workspace.actor")}</span>
            <input
              min="1"
              onChange={(event) => updateFilter("actorUserId", event.target.value)}
              type="number"
              value={filters.actorUserId}
            />
          </label>
          <label className="audit-panel__field">
            <span>{t("workspace.project")}</span>
            <input
              min="1"
              onChange={(event) => updateFilter("projectId", event.target.value)}
              type="number"
              value={filters.projectId}
            />
          </label>
          <label className="audit-panel__field">
            <span>{t("workspace.from")}</span>
            <input
              onChange={(event) => updateFilter("createdFrom", event.target.value)}
              type="datetime-local"
              value={filters.createdFrom}
            />
          </label>
          <label className="audit-panel__field">
            <span>{t("workspace.to")}</span>
            <input
              onChange={(event) => updateFilter("createdTo", event.target.value)}
              type="datetime-local"
              value={filters.createdTo}
            />
          </label>
        </div>
      ) : null}

      {errorMessage !== null ? (
        <ErrorNotice
          className="audit-panel__error"
          message={errorMessage}
          title={t("workspace.auditUnavailable")}
        />
      ) : null}

      {canLoadAuditEvents && events.length === 0 && !isLoading ? (
        <div className="audit-panel__empty">{t("workspace.noAuditEvents")}</div>
      ) : null}

      {events.length > 0 ? (
        <div className="audit-panel__events">
          {events.map((event) => (
            <article className="audit-panel__event" key={event.id}>
              <div className="audit-panel__event-header">
                <strong>{event.action}</strong>
                <span>{formatTimestamp(event.created_at, i18n.language)}</span>
              </div>
              <div className="audit-panel__event-meta">
                {t("workspace.actorLabel")}: {event.actor_user_id ?? t("workspace.systemActor")} · {t("workspace.targetLabel")}: {event.target_type}
                {event.target_id === null ? "" : `#${event.target_id}`}
              </div>
              {event.details !== null ? (
                <p className="audit-panel__event-details">{event.details}</p>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
