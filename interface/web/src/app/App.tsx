import "./App.css";

import { useEffect } from "react";
import { BrowserRouter, Navigate, NavLink, Route, Routes } from "react-router";

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
import type { UserSummary } from "../shared/types/auth";
import type { UserPreferences } from "../shared/types/preferences";
import type { ProjectSummary, RuntimeInspectionSnapshot } from "../shared/types/project";
import { workspaceNavigationItems } from "./workspace-navigation";

const apiBaseUrl = getApiBaseUrl();
type AppLocale = UserPreferences["locale"];

const appCopy: Record<AppLocale, Record<string, string>> = {
  "en-US": {
    activity: "Activity", admin: "Admin", ai: "AI assistance", apiHealth: "API health", attention: "Attention",
    commandCenter: "Command center", commandCenterDescription: "Project navigation, runtime state, lifecycle actions, preferences, audit, and AI review are available through focused workspace sections.",
    connectedAs: "Connected as", guestTitle: "OrchFlow", lifecycleHealth: "Lifecycle health", noSelection: "No project selected",
    overview: "Overview", profile: "Profile", projects: "Projects", refresh: "Refresh", running: "Running",
    settings: "Settings", signOut: "Sign out", system: "System", tools: "Tools", unknown: "unknown", workspace: "Workspace",
  },
  "pt-BR": {
    activity: "Atividade", admin: "Administracao", ai: "Assistencia de IA", apiHealth: "Saude da API", attention: "Atencao",
    commandCenter: "Centro de comando", commandCenterDescription: "Navegacao de projetos, runtime, lifecycle, preferencias, auditoria e revisao de IA estao disponiveis em secoes focadas da workspace.",
    connectedAs: "Conectado como", guestTitle: "OrchFlow", lifecycleHealth: "Saude do lifecycle", noSelection: "Nenhum projeto selecionado",
    overview: "Visao geral", profile: "Perfil", projects: "Projetos", refresh: "Atualizar", running: "Rodando",
    settings: "Configuracoes", signOut: "Sair", system: "Sistema", tools: "Ferramentas", unknown: "desconhecido", workspace: "Workspace",
  },
};

function countRunningProjects(snapshots: Record<number, RuntimeInspectionSnapshot>): number {
  return Object.values(snapshots).filter((snapshot) => snapshot.status === "running").length;
}

function countAttentionProjects(projects: ProjectSummary[]): number {
  return projects.filter((project) => project.lifecycle_configuration_health !== "complete").length;
}

type AuthenticatedWorkspaceProps = { currentUser: UserSummary; onLogout: () => void; token: string };

function AuthenticatedWorkspace({ currentUser, onLogout, token }: AuthenticatedWorkspaceProps) {
  const adminManagement = useAdminManagement(token, currentUser);
  const auditEvents = useAuditEvents(token, currentUser);
  const userPreferences = useUserPreferences(token);
  const projectWorkspace = useProjectWorkspace(token);
  const refreshProjects = projectWorkspace.refresh;
  const aiAssistance = useAIAssistance(token, projectWorkspace.selectedProject, projectWorkspace.acceptUpdatedProject);
  const { errorMessage, healthStatus, isLoading, lastUpdated, refresh } = useHealthStatus();
  const preferences = userPreferences.preferences;
  const locale = preferences?.locale ?? "pt-BR";
  const copy = appCopy[locale];
  const modelIds = Array.from(new Set([aiAssistance.modelCatalog?.default_model, ...(aiAssistance.modelCatalog?.models.map((model) => model.id) ?? [])].filter((modelId): modelId is string => Boolean(modelId))));

  useEffect(() => { document.documentElement.lang = locale; }, [locale]);
  useEffect(() => {
    if (preferences === null) return;
    const intervalId = window.setInterval(() => { refresh(); refreshProjects(); }, preferences.status_refresh_interval_seconds * 1000);
    return () => window.clearInterval(intervalId);
  }, [preferences, refresh, refreshProjects]);

  const overview = (
    <WorkspaceOverview
      attentionProjectCount={countAttentionProjects(projectWorkspace.projects)} copy={copy} errorMessage={errorMessage}
      healthStatus={healthStatus} isLoading={isLoading} lastUpdated={lastUpdated} onRefreshHealth={refresh}
      onRefreshProjects={projectWorkspace.refresh} projectCount={projectWorkspace.projects.length}
      runningProjectCount={countRunningProjects(projectWorkspace.runtimeSnapshotsByProjectId)} selectedProject={projectWorkspace.selectedProject}
    />
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="topbar__brand"><span className="topbar__mark" aria-hidden="true">OF</span><div><strong>{copy.guestTitle}</strong><span>{copy.workspace}</span></div></div>
        <div className="topbar__status"><span className="topbar__api" data-status={healthStatus?.status ?? "unknown"}>{copy.apiHealth}: {healthStatus?.status ?? (isLoading ? "loading" : copy.unknown)}</span><span className="topbar__user">{copy.connectedAs} {currentUser.username}</span></div>
      </header>
      <div className="workspace-layout">
        <nav className="workspace-navigation" aria-label={copy.workspace}>
          {workspaceNavigationItems(currentUser.role, copy).map((item) => <NavLink className={({ isActive }) => isActive ? "workspace-navigation__link workspace-navigation__link--active" : "workspace-navigation__link"} key={item.to} to={item.to}>{item.label}</NavLink>)}
        </nav>
        <section className="workspace-page">
          <Routes>
            <Route path="/overview" element={overview} />
            <Route path="/projects" element={<ProjectWorkspaceRoute copy={copy} currentUser={currentUser} onLogout={onLogout} preferences={preferences} projectWorkspace={projectWorkspace} />} />
            <Route path="/ai" element={<AIAssistancePanel canUseAIAssistance={aiAssistance.canUseAIAssistance} errorMessage={aiAssistance.errorMessage} isApplying={aiAssistance.isApplying} isCreatingProposal={aiAssistance.isCreatingProposal} isLoadingStatus={aiAssistance.isLoadingStatus} isReviewing={aiAssistance.isReviewing} message={aiAssistance.message} modelIds={modelIds} onApplyProposal={aiAssistance.applyProposal} onCreateProposal={(input) => aiAssistance.createProposal({ exclude_patterns: input.excludePatterns, include_patterns: input.includePatterns, intended_operation: input.intendedOperation, max_file_size_bytes: input.maxFileSizeBytes, max_total_bytes: input.maxTotalBytes, selected_model: input.selectedModel }, input.userInstructions)} onRefreshStatus={aiAssistance.refreshStatus} onReviewProposal={aiAssistance.reviewProposal} proposal={aiAssistance.proposal} readyForRequests={aiAssistance.status?.ready_for_requests ?? false} reviewDecision={aiAssistance.review?.decision ?? null} selectedProject={projectWorkspace.selectedProject} statusMessage={aiAssistance.status?.message ?? null} />} />
            <Route path="/activity" element={<AuditEventsPanel canLoadAuditEvents={auditEvents.canLoadAuditEvents} errorMessage={auditEvents.errorMessage} events={auditEvents.events} filters={auditEvents.filters} isLoading={auditEvents.isLoading} onRefresh={auditEvents.refresh} onUpdateFilters={auditEvents.setFilters} />} />
            <Route path="/settings" element={<UserPreferencesPanel errorMessage={userPreferences.errorMessage} isLoading={userPreferences.isLoading} isSaving={userPreferences.isSaving} message={userPreferences.message} onRefresh={userPreferences.refresh} onUpdate={userPreferences.update} preferences={preferences} />} />
            <Route path="/profile" element={<section className="profile-card" aria-label={copy.profile}><span className="workspace-eyebrow">{copy.profile}</span><h1>{currentUser.username}</h1><p>{currentUser.role}</p><button type="button" onClick={onLogout}>{copy.signOut}</button></section>} />
            {currentUser.role === "admin" ? <Route path="/admin" element={<AdminManagementPanel canManage={adminManagement.canManage} currentUser={currentUser} errorMessage={adminManagement.errorMessage} isLoading={adminManagement.isLoading} isMutating={adminManagement.isMutating} onAddOwner={adminManagement.addOwner} onChangeUserActivation={adminManagement.changeUserActivation} onChangeUserRole={adminManagement.changeUserRole} onRefreshProject={projectWorkspace.refresh} onRefreshUsers={adminManagement.refreshUsers} onRemoveOwner={adminManagement.removeOwner} selectedProject={projectWorkspace.selectedProject} successMessage={adminManagement.successMessage} users={adminManagement.users} />} /> : null}
            <Route path="*" element={<Navigate replace to="/overview" />} />
          </Routes>
        </section>
      </div>
    </main>
  );
}

type WorkspaceOverviewProps = {
  attentionProjectCount: number; copy: Record<string, string>; errorMessage: string | null;
  healthStatus: ReturnType<typeof useHealthStatus>["healthStatus"]; isLoading: boolean; lastUpdated: Date | null;
  onRefreshHealth: () => void; onRefreshProjects: () => void; projectCount: number; runningProjectCount: number; selectedProject: ProjectSummary | null;
};

function WorkspaceOverview({ attentionProjectCount, copy, errorMessage, healthStatus, isLoading, lastUpdated, onRefreshHealth, onRefreshProjects, projectCount, runningProjectCount, selectedProject }: WorkspaceOverviewProps) {
  return <div className="workspace-overview"><section className="command-bar" aria-label={copy.commandCenter}><div className="command-bar__summary"><span className="workspace-eyebrow">{copy.commandCenter}</span><h1>{selectedProject?.reference_name ?? copy.noSelection}</h1><p>{copy.commandCenterDescription}</p></div><dl className="command-bar__metrics"><div><dt>{copy.projects}</dt><dd>{projectCount}</dd></div><div><dt>{copy.running}</dt><dd>{runningProjectCount}</dd></div><div><dt>{copy.attention}</dt><dd>{attentionProjectCount}</dd></div><div><dt>{copy.lifecycleHealth}</dt><dd>{selectedProject?.lifecycle_configuration_health ?? "-"}</dd></div></dl><div className="command-bar__actions"><button type="button" onClick={onRefreshProjects}>{copy.refresh}</button><button type="button" onClick={onRefreshHealth}>{copy.system}</button></div></section><HealthCheckCard apiBaseUrl={apiBaseUrl} errorMessage={errorMessage} healthStatus={healthStatus} isLoading={isLoading} lastUpdated={lastUpdated} onRefresh={onRefreshHealth} /></div>;
}

type ProjectWorkspaceRouteProps = { copy: Record<string, string>; currentUser: UserSummary; onLogout: () => void; preferences: UserPreferences | null; projectWorkspace: ReturnType<typeof useProjectWorkspace> };

function ProjectWorkspaceRoute({ copy, currentUser, onLogout, preferences, projectWorkspace }: ProjectWorkspaceRouteProps) {
  return <section className="project-workspace-route" aria-label={copy.projects}><ProjectListPanel currentUser={currentUser} errorMessage={projectWorkspace.errorMessage} isLoading={projectWorkspace.isLoadingProjects} isRegisteringProject={projectWorkspace.isRegisteringProject} onRefresh={projectWorkspace.refresh} onRegisterProject={projectWorkspace.submitProjectRegistration} onSearchQueryChange={projectWorkspace.setSearchQuery} onSelectProject={projectWorkspace.selectProject} projectViewMode={preferences?.project_view_mode ?? "list"} projects={projectWorkspace.projects} registrationMessage={projectWorkspace.registrationMessage} runtimeSnapshotsByProjectId={projectWorkspace.runtimeSnapshotsByProjectId} searchQuery={projectWorkspace.searchQuery} selectedProjectId={projectWorkspace.selectedProjectId} /><ProjectDetailPanel activeAction={projectWorkspace.activeAction} configurationMessage={projectWorkspace.configurationMessage} currentUser={currentUser} errorMessage={projectWorkspace.errorMessage} isLoadingDetail={projectWorkspace.isLoadingDetail} isReloadingProject={projectWorkspace.isReloadingProject} isUnlinkingProject={projectWorkspace.isUnlinkingProject} isUpdatingProject={projectWorkspace.isUpdatingProject} isUpdatingLifecycleConfiguration={projectWorkspace.isUpdatingLifecycleConfiguration} lifecycleResult={projectWorkspace.lifecycleResult} onLogout={onLogout} onRefreshProject={projectWorkspace.refresh} onReloadProject={projectWorkspace.reloadSelectedProject} onRunLifecycleAction={projectWorkspace.runLifecycleAction} onUnlinkProject={projectWorkspace.unlinkSelectedProject} onUpdateLifecycleConfiguration={projectWorkspace.updateLifecycleConfiguration} onUpdateProject={projectWorkspace.updateSelectedProject} projectUpdateMessage={projectWorkspace.projectUpdateMessage} runtimeSnapshot={projectWorkspace.runtimeSnapshot} selectedProject={projectWorkspace.selectedProject} unlinkMessage={projectWorkspace.unlinkMessage} /></section>;
}

export function App() {
  const authSession = useAuthSession();
  useEffect(() => { if (authSession.currentUser === null) document.documentElement.lang = "en-US"; }, [authSession.currentUser]);
  if (authSession.currentUser === null || authSession.token === null) return <main className="app-shell app-shell--auth"><section className="auth-screen"><LoginPanel errorMessage={authSession.errorMessage} isLoading={authSession.isLoading} onCreateAccount={authSession.createAccount} onSubmit={authSession.login} statusMessage={authSession.statusMessage} /></section></main>;
  return <BrowserRouter><AuthenticatedWorkspace currentUser={authSession.currentUser} onLogout={authSession.logout} token={authSession.token} /></BrowserRouter>;
}

export default App;
