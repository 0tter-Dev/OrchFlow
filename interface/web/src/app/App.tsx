import "./App.css";

import { useEffect } from "react";

import { AdminManagementPanel } from "../features/admin/components/AdminManagementPanel";
import { useAdminManagement } from "../features/admin/hooks/useAdminManagement";
import { AIAssistancePanel } from "../features/ai/components/AIAssistancePanel";
import { useAIAssistance } from "../features/ai/hooks/useAIAssistance";
import { AuditEventsPanel } from "../features/audit/components/AuditEventsPanel";
import { useAuditEvents } from "../features/audit/hooks/useAuditEvents";
import { LoginPanel } from "../features/auth/components/LoginPanel";
import { useAuthSession } from "../features/auth/hooks/useAuthSession";
import { UserPreferencesPanel } from "../features/preferences/components/UserPreferencesPanel";
import { useUserPreferences } from "../features/preferences/hooks/useUserPreferences";
import { ProjectDetailPanel } from "../features/projects/components/ProjectDetailPanel";
import { ProjectListPanel } from "../features/projects/components/ProjectListPanel";
import { useProjectWorkspace } from "../features/projects/hooks/useProjectWorkspace";
import { HealthCheckCard } from "../features/system-health/components/HealthCheckCard";
import { useHealthStatus } from "../features/system-health/hooks/useHealthStatus";
import { getApiBaseUrl } from "../shared/config/env";
import type { UserPreferences } from "../shared/types/preferences";
import type { ProjectSummary, RuntimeInspectionSnapshot } from "../shared/types/project";

const apiBaseUrl = getApiBaseUrl();

type AppLocale = UserPreferences["locale"];

const appCopy: Record<
  AppLocale,
  {
    apiHealth: string;
    attention: string;
    commandCenter: string;
    commandCenterDescription: string;
    connectedAs: string;
    guestFocus: string;
    guestFocusCopy: string;
    guestTitle: string;
    lifecycleHealth: string;
    noSelection: string;
    projects: string;
    refresh: string;
    running: string;
    system: string;
    tools: string;
    unknown: string;
    workspace: string;
  }
> = {
  "en-US": {
    apiHealth: "API health",
    attention: "Attention",
    commandCenter: "Command center",
    commandCenterDescription:
      "Project navigation, runtime state, lifecycle actions, preferences, audit, and AI review stay in one compact operator surface.",
    connectedAs: "Connected as",
    guestFocus: "Local operator login",
    guestFocusCopy:
      "Sign in to open the project workspace, inspect visible runtime status, and operate configured lifecycle actions.",
    guestTitle: "OrchFlow",
    lifecycleHealth: "Lifecycle health",
    noSelection: "No project selected",
    projects: "Projects",
    refresh: "Refresh",
    running: "Running",
    system: "System",
    tools: "Tools",
    unknown: "unknown",
    workspace: "Workspace",
  },
  "pt-BR": {
    apiHealth: "Saude da API",
    attention: "Atencao",
    commandCenter: "Centro de comando",
    commandCenterDescription:
      "Navegacao de projetos, runtime, lifecycle, preferencias, auditoria e revisao de IA ficam em uma superficie operacional compacta.",
    connectedAs: "Conectado como",
    guestFocus: "Login do operador local",
    guestFocusCopy:
      "Entre para abrir o workspace de projetos, inspecionar runtime visivel e operar acoes de lifecycle configuradas.",
    guestTitle: "OrchFlow",
    lifecycleHealth: "Saude do lifecycle",
    noSelection: "Nenhum projeto selecionado",
    projects: "Projetos",
    refresh: "Atualizar",
    running: "Rodando",
    system: "Sistema",
    tools: "Ferramentas",
    unknown: "desconhecido",
    workspace: "Workspace",
  },
};

function countRunningProjects(
  runtimeSnapshotsByProjectId: Record<number, RuntimeInspectionSnapshot>,
): number {
  return Object.values(runtimeSnapshotsByProjectId).filter(
    (snapshot) => snapshot.status === "running",
  ).length;
}

function countAttentionProjects(projects: ProjectSummary[]): number {
  return projects.filter(
    (project) => project.lifecycle_configuration_health !== "complete",
  ).length;
}

export function App() {
  const authSession = useAuthSession();
  const adminManagement = useAdminManagement(authSession.token, authSession.currentUser);
  const auditEvents = useAuditEvents(authSession.token, authSession.currentUser);
  const userPreferences = useUserPreferences(authSession.token);
  const projectWorkspace = useProjectWorkspace(authSession.token);
  const aiAssistance = useAIAssistance(
    authSession.token,
    projectWorkspace.selectedProject,
    projectWorkspace.acceptUpdatedProject,
  );
  const aiModelIds = Array.from(
    new Set(
      [
        aiAssistance.modelCatalog?.default_model,
        ...(aiAssistance.modelCatalog?.models.map((model) => model.id) ?? []),
      ].filter((modelId): modelId is string => Boolean(modelId && modelId.length > 0)),
    ),
  );
  const { errorMessage, healthStatus, isLoading, lastUpdated, refresh } = useHealthStatus();
  const preferences = userPreferences.preferences;
  const locale = preferences?.locale ?? "pt-BR";
  const copy = appCopy[locale];
  const refreshProjects = projectWorkspace.refresh;
  const projectCount = projectWorkspace.projects.length;
  const runningProjectCount = countRunningProjects(projectWorkspace.runtimeSnapshotsByProjectId);
  const attentionProjectCount = countAttentionProjects(projectWorkspace.projects);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  useEffect(() => {
    if (authSession.currentUser === null || preferences === null) {
      return;
    }

    const intervalId = window.setInterval(() => {
      refresh();
      refreshProjects();
    }, preferences.status_refresh_interval_seconds * 1000);

    return () => window.clearInterval(intervalId);
  }, [authSession.currentUser, preferences, refresh, refreshProjects]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="topbar__brand">
          <span className="topbar__mark" aria-hidden="true">
            OF
          </span>
          <div>
            <strong>{copy.guestTitle}</strong>
            <span>{copy.workspace}</span>
          </div>
        </div>
        <div className="topbar__status">
          <span className="topbar__api" data-status={healthStatus?.status ?? "unknown"}>
            {copy.apiHealth}: {healthStatus?.status ?? (isLoading ? "loading" : copy.unknown)}
          </span>
          {authSession.currentUser !== null ? (
            <span className="topbar__user">
              {copy.connectedAs} {authSession.currentUser.username}
            </span>
          ) : null}
        </div>
      </header>

      {authSession.currentUser === null ? (
        <section className="guest-workspace">
          <div className="guest-workspace__intro">
            <span className="workspace-eyebrow">{copy.guestFocus}</span>
            <h1>{copy.guestTitle}</h1>
            <p>{copy.guestFocusCopy}</p>
          </div>
          <div className="guest-workspace__grid">
            <LoginPanel
              errorMessage={authSession.errorMessage}
              isLoading={authSession.isLoading}
              onSubmit={authSession.login}
            />
            <HealthCheckCard
              apiBaseUrl={apiBaseUrl}
              errorMessage={errorMessage}
              healthStatus={healthStatus}
              isLoading={isLoading}
              lastUpdated={lastUpdated}
              onRefresh={refresh}
            />
          </div>
        </section>
      ) : (
        <section className="operator-workspace">
          <ProjectListPanel
            currentUser={authSession.currentUser}
            errorMessage={projectWorkspace.errorMessage}
            isLoading={projectWorkspace.isLoadingProjects}
            isRegisteringProject={projectWorkspace.isRegisteringProject}
            onRefresh={projectWorkspace.refresh}
            onRegisterProject={projectWorkspace.submitProjectRegistration}
            onSearchQueryChange={projectWorkspace.setSearchQuery}
            onSelectProject={projectWorkspace.selectProject}
            projectViewMode={preferences?.project_view_mode ?? "list"}
            projects={projectWorkspace.projects}
            registrationMessage={projectWorkspace.registrationMessage}
            runtimeSnapshotsByProjectId={projectWorkspace.runtimeSnapshotsByProjectId}
            searchQuery={projectWorkspace.searchQuery}
            selectedProjectId={projectWorkspace.selectedProjectId}
          />

          <div className="operator-workspace__main">
            <section className="command-bar" aria-label={copy.commandCenter}>
              <div className="command-bar__summary">
                <span className="workspace-eyebrow">{copy.commandCenter}</span>
                <h1>{projectWorkspace.selectedProject?.reference_name ?? copy.noSelection}</h1>
                <p>{copy.commandCenterDescription}</p>
              </div>
              <dl className="command-bar__metrics">
                <div>
                  <dt>{copy.projects}</dt>
                  <dd>{projectCount}</dd>
                </div>
                <div>
                  <dt>{copy.running}</dt>
                  <dd>{runningProjectCount}</dd>
                </div>
                <div>
                  <dt>{copy.attention}</dt>
                  <dd>{attentionProjectCount}</dd>
                </div>
                <div>
                  <dt>{copy.lifecycleHealth}</dt>
                  <dd>{projectWorkspace.selectedProject?.lifecycle_configuration_health ?? "-"}</dd>
                </div>
              </dl>
              <div className="command-bar__actions">
                <button type="button" onClick={projectWorkspace.refresh}>
                  {copy.refresh}
                </button>
                <button type="button" onClick={refresh}>
                  {copy.system}
                </button>
              </div>
            </section>

            <div className="workspace-content">
              <div className="workspace-content__primary">
                <ProjectDetailPanel
                  activeAction={projectWorkspace.activeAction}
                  configurationMessage={projectWorkspace.configurationMessage}
                  currentUser={authSession.currentUser}
                  errorMessage={projectWorkspace.errorMessage}
                  isLoadingDetail={projectWorkspace.isLoadingDetail}
                  isReloadingProject={projectWorkspace.isReloadingProject}
                  isUpdatingProject={projectWorkspace.isUpdatingProject}
                  isUpdatingLifecycleConfiguration={
                    projectWorkspace.isUpdatingLifecycleConfiguration
                  }
                  lifecycleResult={projectWorkspace.lifecycleResult}
                  onLogout={authSession.logout}
                  onRefreshProject={projectWorkspace.refresh}
                  onReloadProject={projectWorkspace.reloadSelectedProject}
                  onRunLifecycleAction={projectWorkspace.runLifecycleAction}
                  onUpdateProject={projectWorkspace.updateSelectedProject}
                  onUpdateLifecycleConfiguration={
                    projectWorkspace.updateLifecycleConfiguration
                  }
                  projectUpdateMessage={projectWorkspace.projectUpdateMessage}
                  runtimeSnapshot={projectWorkspace.runtimeSnapshot}
                  selectedProject={projectWorkspace.selectedProject}
                />
              </div>

              <aside className="workspace-content__rail" aria-label={copy.tools}>
                <HealthCheckCard
                  apiBaseUrl={apiBaseUrl}
                  errorMessage={errorMessage}
                  healthStatus={healthStatus}
                  isLoading={isLoading}
                  lastUpdated={lastUpdated}
                  onRefresh={refresh}
                />
                <UserPreferencesPanel
                  errorMessage={userPreferences.errorMessage}
                  isLoading={userPreferences.isLoading}
                  isSaving={userPreferences.isSaving}
                  message={userPreferences.message}
                  onRefresh={userPreferences.refresh}
                  onUpdate={userPreferences.update}
                  preferences={preferences}
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
                <AIAssistancePanel
                  canUseAIAssistance={aiAssistance.canUseAIAssistance}
                  errorMessage={aiAssistance.errorMessage}
                  isApplying={aiAssistance.isApplying}
                  isCreatingProposal={aiAssistance.isCreatingProposal}
                  isLoadingStatus={aiAssistance.isLoadingStatus}
                  isReviewing={aiAssistance.isReviewing}
                  message={aiAssistance.message}
                  modelIds={aiModelIds}
                  onApplyProposal={aiAssistance.applyProposal}
                  onCreateProposal={(input) =>
                    aiAssistance.createProposal(
                      {
                        exclude_patterns: input.excludePatterns,
                        include_patterns: input.includePatterns,
                        intended_operation: input.intendedOperation,
                        max_file_size_bytes: input.maxFileSizeBytes,
                        max_total_bytes: input.maxTotalBytes,
                        selected_model: input.selectedModel,
                      },
                      input.userInstructions,
                    )
                  }
                  onRefreshStatus={aiAssistance.refreshStatus}
                  onReviewProposal={aiAssistance.reviewProposal}
                  proposal={aiAssistance.proposal}
                  readyForRequests={aiAssistance.status?.ready_for_requests ?? false}
                  reviewDecision={aiAssistance.review?.decision ?? null}
                  selectedProject={projectWorkspace.selectedProject}
                  statusMessage={aiAssistance.status?.message ?? null}
                />
                <AuditEventsPanel
                  canLoadAuditEvents={auditEvents.canLoadAuditEvents}
                  errorMessage={auditEvents.errorMessage}
                  events={auditEvents.events}
                  filters={auditEvents.filters}
                  isLoading={auditEvents.isLoading}
                  onRefresh={auditEvents.refresh}
                  onUpdateFilters={auditEvents.setFilters}
                />
              </aside>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
