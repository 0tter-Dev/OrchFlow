import "./App.css";

import { HealthCheckCard } from "../features/system-health/components/HealthCheckCard";
import { useHealthStatus } from "../features/system-health/hooks/useHealthStatus";
import { getApiBaseUrl } from "../shared/config/env";

const apiBaseUrl = getApiBaseUrl();

export function App() {
  const { errorMessage, healthStatus, isLoading, lastUpdated, refresh } = useHealthStatus();

  return (
    <main className="app-shell">
      <div className="app-frame">
        <section className="hero">
          <span className="hero__eyebrow">OrchFlow Web Bootstrap</span>
          <div>
            <h1 className="hero__title">A base visual para operar OrchFlow com clareza.</h1>
            <p className="hero__copy">
              Este primeiro bootstrap do cliente web valida a fronteira de consumo da API,
              consolida o stack `React` + `TypeScript` + `Vite` + `pnpm` e deixa pronta a
              fundação para o fluxo de autenticação, projetos e lifecycle do próximo PR.
            </p>
          </div>

          <div className="hero__meta">
            <article className="meta-card">
              <span className="meta-card__label">API Base URL</span>
              <strong className="meta-card__value">{apiBaseUrl}</strong>
            </article>
            <article className="meta-card">
              <span className="meta-card__label">Current Focus</span>
              <strong className="meta-card__value">Health check + interface foundation</strong>
            </article>
          </div>
        </section>

        <section className="canvas">
          <HealthCheckCard
            apiBaseUrl={apiBaseUrl}
            errorMessage={errorMessage}
            healthStatus={healthStatus}
            isLoading={isLoading}
            lastUpdated={lastUpdated}
            onRefresh={refresh}
          />

          <aside className="panel">
            <h2 className="panel__title">What this PR leaves ready</h2>
            <p className="panel__copy">
              The web boundary is now bootstrapped around the same backend contracts already
              available in the project. The next step can focus on real operator flows instead
              of setup churn.
            </p>
            <ul className="panel__list">
              <li>API client boundary isolated in shared code</li>
              <li>Feature-oriented folder structure for the web client</li>
              <li>Frontend lint, test, and build scripts aligned with `pnpm`</li>
              <li>Initial visual surface for validating local integration quickly</li>
            </ul>
          </aside>
        </section>
      </div>
    </main>
  );
}

export default App;
