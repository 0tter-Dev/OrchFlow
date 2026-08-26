import "./AuditEventsPanel.css";

import type { AuditEventSummary } from "../../../shared/types/audit";

type AuditEventsPanelProps = {
  canLoadAuditEvents: boolean;
  errorMessage: string | null;
  events: AuditEventSummary[];
  isLoading: boolean;
  onRefresh: () => void;
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
  isLoading,
  onRefresh,
}: AuditEventsPanelProps) {
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

      {errorMessage !== null ? <div className="audit-panel__error">{errorMessage}</div> : null}

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
