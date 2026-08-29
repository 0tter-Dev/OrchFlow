import "./App.css";

import { AdminManagementPanel } from "../features/admin/components/AdminManagementPanel";
import { useAdminManagement } from "../features/admin/hooks/useAdminManagement";
import { AuditEventsPanel } from "../features/audit/components/AuditEventsPanel";
import { useAuditEvents } from "../features/audit/hooks/useAuditEvents";
import { LoginPanel } from "../features/auth/components/LoginPanel";
import { useAuthSession } from "../features/auth/hooks/useAuthSession";
import { ProjectDetailPanel } from "../features/projects/components/ProjectDetailPanel";
import { ProjectListPanel } from "../features/projects/components/ProjectListPanel";
import { useProjectWorkspace } from "../features/projects/hooks/useProjectWorkspace";
import { HealthCheckCard } from "../features/system-health/components/HealthCheckCard";
import { useHealthStatus } from "../features/system-health/hooks/useHealthStatus";
import { getApiBaseUrl } from "../shared/config/env";

const apiBaseUrl = getApiBaseUrl();

export function App() {
  const authSession = useAuthSession();
  const adminManagement = useAdminManagement(authSession.token, authSession.currentUser);
  const auditEvents = useAuditEvents(authSession.token, authSession.currentUser);
  const projectWorkspace = useProjectWorkspace(authSession.token);
  const { errorMessage, healthStatus, isLoading, lastUpdated, refresh } = useHealthStatus();

  return (
    <main className="app-shell">
      <div className="app-frame">
        <section className="hero">
          <div className="hero__topline">
            <span className="hero__eyebrow">OrchFlow Web Operator Surface</span>
            <span className="hero__status">
              <span className="hero__status-dot" data-status={healthStatus?.status ?? "unknown"} />
              API health: {healthStatus?.status ?? (isLoading ? "loading" : "unknown")}
            </span>
          </div>
          <div>
            <h1 className="hero__title">Register and operate projects through the web flow.</h1>
            <p className="hero__copy">
              The web client now consumes the same backend contracts already stabilized in API and
              CLI. This stage brings existing-project registration, project visibility, runtime
              inspection, and lifecycle controls into one operator-focused workspace.
            </p>
          </div>

          <div className="hero__meta">
            <article className="meta-card">
              <span className="meta-card__label">API Base URL</span>
              <strong className="meta-card__value">{apiBaseUrl}</strong>
            </article>
            <article className="meta-card">
              <span className="meta-card__label">Current Focus</span>
              <strong className="meta-card__value">Auth, projects, runtime, and lifecycle</strong>
            </article>
          </div>
        </section>

        {authSession.currentUser === null ? (
          <section className="guest-layout">
            <HealthCheckCard
              apiBaseUrl={apiBaseUrl}
              errorMessage={errorMessage}
              healthStatus={healthStatus}
              isLoading={isLoading}
              lastUpdated={lastUpdated}
              onRefresh={refresh}
            />

            <div className="support-panel">
              <LoginPanel
                errorMessage={authSession.errorMessage}
                isLoading={authSession.isLoading}
                onSubmit={authSession.login}
              />
              <aside className="support-panel__card">
                <h2 className="support-panel__title">What this stage unlocks</h2>
                <p className="support-panel__copy">
                  Once authenticated, the web client moves beyond the bootstrap health-check and
                  starts acting as a practical operator surface for already managed projects.
                </p>
                <ul className="support-panel__list">
                  <li>Load the same authenticated project registry exposed by the API and CLI</li>
                  <li>Inspect runtime state without leaving the browser</li>
                  <li>Trigger `status`, `start`, `stop`, and `restart` from the same workspace</li>
                  <li>Keep the frontend aligned with the documented local-first scope</li>
                </ul>
              </aside>
            </div>
          </section>
        ) : (
          <section className="workspace-layout">
            <ProjectListPanel
              currentUser={authSession.currentUser}
              errorMessage={projectWorkspace.errorMessage}
              isLoading={projectWorkspace.isLoadingProjects}
              isRegisteringProject={projectWorkspace.isRegisteringProject}
              onRefresh={projectWorkspace.refresh}
              onRegisterProject={projectWorkspace.submitProjectRegistration}
              onSearchQueryChange={projectWorkspace.setSearchQuery}
              onSelectProject={projectWorkspace.selectProject}
              projects={projectWorkspace.projects}
              registrationMessage={projectWorkspace.registrationMessage}
              searchQuery={projectWorkspace.searchQuery}
              selectedProjectId={projectWorkspace.selectedProjectId}
            />

            <div className="support-panel">
              <ProjectDetailPanel
                activeAction={projectWorkspace.activeAction}
                configurationMessage={projectWorkspace.configurationMessage}
                currentUser={authSession.currentUser}
                errorMessage={projectWorkspace.errorMessage}
                isLoadingDetail={projectWorkspace.isLoadingDetail}
                isReloadingProject={projectWorkspace.isReloadingProject}
                isUpdatingLifecycleConfiguration={
                  projectWorkspace.isUpdatingLifecycleConfiguration
                }
                lifecycleResult={projectWorkspace.lifecycleResult}
                onLogout={authSession.logout}
                onRefreshProject={projectWorkspace.refresh}
                onReloadProject={projectWorkspace.reloadSelectedProject}
                onRunLifecycleAction={projectWorkspace.runLifecycleAction}
                onUpdateLifecycleConfiguration={
                  projectWorkspace.updateLifecycleConfiguration
                }
                runtimeSnapshot={projectWorkspace.runtimeSnapshot}
                selectedProject={projectWorkspace.selectedProject}
              />
              <HealthCheckCard
                apiBaseUrl={apiBaseUrl}
                errorMessage={errorMessage}
                healthStatus={healthStatus}
                isLoading={isLoading}
                lastUpdated={lastUpdated}
                onRefresh={refresh}
              />
              <AdminManagementPanel
                canManage={adminManagement.canManage}
                currentUser={authSession.currentUser}
                errorMessage={adminManagement.errorMessage}
                isLoading={adminManagement.isLoading}
                isMutating={adminManagement.isMutating}
                onAddOwner={adminManagement.addOwner}
                onChangeUserActivation={adminManagement.changeUserActivation}
                onChangeUserRole={adminManagement.changeUserRole}
                onRefreshProject={projectWorkspace.refresh}
                onRefreshUsers={adminManagement.refreshUsers}
                onRemoveOwner={adminManagement.removeOwner}
                selectedProject={projectWorkspace.selectedProject}
                successMessage={adminManagement.successMessage}
                users={adminManagement.users}
              />
              <AuditEventsPanel
                canLoadAuditEvents={auditEvents.canLoadAuditEvents}
                errorMessage={auditEvents.errorMessage}
                events={auditEvents.events}
                isLoading={auditEvents.isLoading}
                onRefresh={auditEvents.refresh}
              />
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

export default App;
