import type { SystemHealthSnapshot } from "../../../shared/types/system";
import "./HealthCheckCard.css";
import { ErrorNotice } from "../../../shared/components/ErrorNotice";

type HealthCheckCardProps = {
  apiBaseUrl: string;
  errorMessage: string | null;
  healthStatus: SystemHealthSnapshot | null;
  isLoading: boolean;
  lastUpdated: Date | null;
  onRefresh: () => void;
};

function formatLastUpdated(lastUpdated: Date | null): string {
  if (lastUpdated === null) {
    return "Not refreshed yet";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(lastUpdated);
}

export function HealthCheckCard({
  apiBaseUrl,
  errorMessage,
  healthStatus,
  isLoading,
  lastUpdated,
  onRefresh,
}: HealthCheckCardProps) {
  return (
    <section className="health-card">
      <header className="health-card__header">
        <div>
          <span className="health-card__eyebrow">System probe</span>
          <h2 className="health-card__title">Backend status</h2>
        </div>
        <button className="health-card__button" type="button" onClick={onRefresh}>
          Refresh
        </button>
      </header>

      <div className="health-card__surface">
        <div className="health-card__summary">
          <div>
            <span className="health-card__label">Target</span>
            <strong>{apiBaseUrl}/health</strong>
          </div>
          <div>
            <span className="health-card__label">Last updated</span>
            <strong>{formatLastUpdated(lastUpdated)}</strong>
          </div>
        </div>

        {isLoading ? (
          <p className="health-card__message">Inspecting the OrchFlow API health endpoint...</p>
        ) : null}

        {errorMessage !== null ? (
          <ErrorNotice
            className="health-card__error"
            message={errorMessage}
            title="Unable to reach the OrchFlow API."
          />
        ) : null}

        {healthStatus !== null ? (
          <dl className="health-card__metrics">
            <div>
              <dt>Name</dt>
              <dd>{healthStatus.name}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd data-status={healthStatus.status}>{healthStatus.status}</dd>
            </div>
            <div>
              <dt>Stage</dt>
              <dd>{healthStatus.stage}</dd>
            </div>
            <div>
              <dt>Version</dt>
              <dd>{healthStatus.version}</dd>
            </div>
          </dl>
        ) : null}
      </div>
    </section>
  );
}
