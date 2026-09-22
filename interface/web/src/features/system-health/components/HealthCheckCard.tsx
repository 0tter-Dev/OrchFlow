import { RefreshCw } from "lucide-react";
import { useTranslation } from "react-i18next";
import "../../../app/i18n";

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

function formatLastUpdated(lastUpdated: Date | null, locale: string, emptyLabel: string): string {
  if (lastUpdated === null) {
    return emptyLabel;
  }

  return new Intl.DateTimeFormat(locale, {
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
  const { i18n, t } = useTranslation();
  const hasHealthSnapshot = healthStatus !== null;
  const isInitialLoad = isLoading && !hasHealthSnapshot;
  const isRefreshingSnapshot = isLoading && hasHealthSnapshot;

  return (
    <section className="health-card">
      <header className="health-card__header">
        <div>
          <span className="health-card__eyebrow">{t("workspace.systemProbe")}</span>
          <h2 className="health-card__title">{t("workspace.backendStatus")}</h2>
        </div>
        <button className="health-card__button" type="button" onClick={onRefresh}>
          <RefreshCw aria-hidden="true" size={15} strokeWidth={2.4} />
          {isRefreshingSnapshot ? t("workspace.preferencesSaving") : t("workspace.refresh")}
        </button>
      </header>

      <div className="health-card__surface">
        <div className="health-card__summary">
          <div>
            <span className="health-card__label">{t("workspace.target")}</span>
            <strong>{apiBaseUrl}/health</strong>
          </div>
          <div>
            <span className="health-card__label">{t("workspace.lastUpdated")}</span>
            <strong>{formatLastUpdated(lastUpdated, i18n.language, t("workspace.notRefreshedYet"))}</strong>
          </div>
        </div>

        {isInitialLoad ? (
          <p className="health-card__message">{t("workspace.inspectingHealth")}</p>
        ) : null}

        {isRefreshingSnapshot ? (
          <p className="health-card__message">{t("workspace.refreshingHealth")}</p>
        ) : null}

        {errorMessage !== null ? (
          <ErrorNotice
            className="health-card__error"
            message={errorMessage}
            title={t("workspace.apiUnavailable")}
          />
        ) : null}

        {hasHealthSnapshot ? (
          <dl className="health-card__metrics">
            <div>
              <dt>{t("workspace.name")}</dt>
              <dd>{healthStatus.name}</dd>
            </div>
            <div>
              <dt>{t("workspace.status")}</dt>
              <dd data-status={healthStatus.status}>{healthStatus.status}</dd>
            </div>
            <div>
              <dt>{t("workspace.stage")}</dt>
              <dd>{healthStatus.stage}</dd>
            </div>
            <div>
              <dt>{t("workspace.version")}</dt>
              <dd>{healthStatus.version}</dd>
            </div>
          </dl>
        ) : null}
      </div>
    </section>
  );
}
