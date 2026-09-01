import "./AuditEventsPanel.css";

import type { Dispatch, SetStateAction } from "react";

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

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
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
  const updateFilter = (name: keyof AuditEventFilters, value: string) => {
    onUpdateFilters((currentFilters) => ({ ...currentFilters, [name]: value }));
  };

  return (
    <section className="audit-panel">
      <header className="audit-panel__header">
        <div>
          <span className="audit-panel__eyebrow">Audit history</span>
          <h2 className="audit-panel__title">Recent operational events</h2>
        </div>
        <button
          className="audit-panel__button"
          disabled={!canLoadAuditEvents || isLoading}
          onClick={onRefresh}
          type="button"
        >
          {isLoading ? "Loading..." : "Refresh"}
        </button>
      </header>

      {!canLoadAuditEvents ? (
        <div className="audit-panel__empty">Admin role is required to view audit history.</div>
      ) : null}

      {canLoadAuditEvents ? (
        <div className="audit-panel__filters">
          <label className="audit-panel__field">
            <span>Limit</span>
            <input
              min="1"
              max="100"
              onChange={(event) => updateFilter("limit", event.target.value)}
              type="number"
              value={filters.limit}
            />
          </label>
          <label className="audit-panel__field">
            <span>Action</span>
            <input
              onChange={(event) => updateFilter("action", event.target.value)}
              placeholder="project.register"
              value={filters.action}
            />
          </label>
          <label className="audit-panel__field">
            <span>Actor</span>
            <input
              min="1"
              onChange={(event) => updateFilter("actorUserId", event.target.value)}
              type="number"
              value={filters.actorUserId}
            />
          </label>
          <label className="audit-panel__field">
            <span>Project</span>
            <input
              min="1"
              onChange={(event) => updateFilter("projectId", event.target.value)}
              type="number"
              value={filters.projectId}
            />
          </label>
          <label className="audit-panel__field">
            <span>From</span>
            <input
              onChange={(event) => updateFilter("createdFrom", event.target.value)}
              type="datetime-local"
              value={filters.createdFrom}
            />
          </label>
          <label className="audit-panel__field">
            <span>To</span>
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
          title="Audit history unavailable"
        />
      ) : null}

      {canLoadAuditEvents && events.length === 0 && !isLoading ? (
        <div className="audit-panel__empty">No audit events are available yet.</div>
      ) : null}

      {events.length > 0 ? (
        <div className="audit-panel__events">
          {events.map((event) => (
            <article className="audit-panel__event" key={event.id}>
              <div className="audit-panel__event-header">
                <strong>{event.action}</strong>
                <span>{formatTimestamp(event.created_at)}</span>
              </div>
              <div className="audit-panel__event-meta">
                actor: {event.actor_user_id ?? "system"} · target: {event.target_type}
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
