import { startTransition, useDeferredValue, useEffect, useEffectEvent, useState } from "react";

import { formatErrorMessage } from "../../../shared/api/errors";
import {
  executeLifecycleAction,
  getProject,
  getRuntimeSnapshot,
  listProjects,
  registerProject,
  reloadProject,
  updateProject,
  updateProjectLifecycleConfiguration,
} from "../../../shared/api/projects";
import type {
  CanonicalLifecycleAction,
  LifecycleExecutionSnapshot,
  ProjectLifecycleConfigurationInput,
  ProjectRegistrationInput,
  ProjectSummary,
  ProjectUpdateInput,
  RuntimeInspectionSnapshot,
} from "../../../shared/types/project";

type ProjectWorkspaceState = {
  activeAction: CanonicalLifecycleAction | null;
  configurationMessage: string | null;
  errorMessage: string | null;
  isReloadingProject: boolean;
  isLoadingDetail: boolean;
  isLoadingProjects: boolean;
  isRegisteringProject: boolean;
  isUpdatingProject: boolean;
  isUpdatingLifecycleConfiguration: boolean;
  lifecycleResult: LifecycleExecutionSnapshot | null;
  projectUpdateMessage: string | null;
  projects: ProjectSummary[];
  registrationMessage: string | null;
  runtimeSnapshot: RuntimeInspectionSnapshot | null;
  searchQuery: string;
  selectedProject: ProjectSummary | null;
  selectedProjectId: number | null;
};

const initialState: ProjectWorkspaceState = {
  activeAction: null,
  configurationMessage: null,
  errorMessage: null,
  isReloadingProject: false,
  isLoadingDetail: false,
  isLoadingProjects: false,
  isRegisteringProject: false,
  isUpdatingProject: false,
  isUpdatingLifecycleConfiguration: false,
  lifecycleResult: null,
  projectUpdateMessage: null,
  projects: [],
  registrationMessage: null,
  runtimeSnapshot: null,
  searchQuery: "",
  selectedProject: null,
  selectedProjectId: null,
};

function replaceProjectInList(projects: ProjectSummary[], project: ProjectSummary) {
  return projects.map((currentProject) =>
    currentProject.id === project.id ? project : currentProject,
  );
}

export function useProjectWorkspace(token: string | null) {
  const [state, setState] = useState<ProjectWorkspaceState>(initialState);
  const deferredSearchQuery = useDeferredValue(state.searchQuery);

  const refreshSelectedProject = useEffectEvent(async (projectId: number, sessionToken: string) => {
    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoadingDetail: true,
    }));

    try {
      const [selectedProject, runtimeSnapshot] = await Promise.all([
        getProject(sessionToken, projectId),
        getRuntimeSnapshot(sessionToken, projectId),
      ]);
      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isLoadingDetail: false,
        runtimeSnapshot,
        selectedProject,
        selectedProjectId: projectId,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to load the selected project."),
        isLoadingDetail: false,
      }));
    }
  });

  const refreshProjects = useEffectEvent(async (sessionToken: string) => {
    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoadingProjects: true,
    }));

    try {
      const projects = await listProjects(sessionToken);
      const nextSelectedProjectId =
        projects.find((project) => project.id === state.selectedProjectId)?.id ??
        projects[0]?.id ??
        null;

      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isLoadingProjects: false,
        projects,
        runtimeSnapshot: nextSelectedProjectId === null ? null : currentState.runtimeSnapshot,
        selectedProject:
          nextSelectedProjectId === null
            ? null
            : currentState.selectedProject?.id === nextSelectedProjectId
              ? currentState.selectedProject
              : null,
        selectedProjectId: nextSelectedProjectId,
      }));

      if (nextSelectedProjectId !== null) {
        void refreshSelectedProject(nextSelectedProjectId, sessionToken);
      }
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to load managed projects."),
        isLoadingProjects: false,
      }));
    }
  });

  useEffect(() => {
    if (token === null) {
      setState(initialState);
      return;
    }

    void refreshProjects(token);
  }, [refreshProjects, token]);

  function selectProject(projectId: number) {
    startTransition(() => {
      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        lifecycleResult: null,
        selectedProjectId: projectId,
      }));
    });

    if (token !== null) {
      void refreshSelectedProject(projectId, token);
    }
  }

  function setSearchQuery(searchQuery: string) {
    setState((currentState) => ({
      ...currentState,
      searchQuery,
    }));
  }

  function acceptUpdatedProject(project: ProjectSummary) {
    setState((currentState) => ({
      ...currentState,
      configurationMessage: `${project.reference_name} updated from approved AI proposal.`,
      lifecycleResult: null,
      projects: replaceProjectInList(currentState.projects, project),
      selectedProject: project,
      selectedProjectId: project.id,
    }));
  }

  const submitProjectRegistration = useEffectEvent(
    async (registrationInput: ProjectRegistrationInput) => {
      if (token === null) {
        return;
      }

      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isRegisteringProject: true,
        registrationMessage: null,
      }));

      try {
        const registeredProject = await registerProject(token, registrationInput);
        const [projects, runtimeSnapshot] = await Promise.all([
          listProjects(token),
          getRuntimeSnapshot(token, registeredProject.id),
        ]);
        const selectedProject =
          projects.find((project) => project.id === registeredProject.id) ?? registeredProject;

        setState((currentState) => ({
          ...currentState,
          errorMessage: null,
          isRegisteringProject: false,
          lifecycleResult: null,
          projects,
          registrationMessage: `${registeredProject.reference_name} registered successfully.`,
          runtimeSnapshot,
          selectedProject,
          selectedProjectId: registeredProject.id,
        }));
      } catch (error) {
        setState((currentState) => ({
          ...currentState,
          errorMessage: formatErrorMessage(error, "Unable to register the project."),
          isRegisteringProject: false,
          registrationMessage: null,
        }));
      }
    },
  );

  const runLifecycleAction = useEffectEvent(async (action: CanonicalLifecycleAction) => {
    if (token === null || state.selectedProjectId === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      activeAction: action,
      errorMessage: null,
    }));

    try {
      const lifecycleResult = await executeLifecycleAction(token, state.selectedProjectId, action);
      const [selectedProject, runtimeSnapshot] = await Promise.all([
        getProject(token, state.selectedProjectId),
        getRuntimeSnapshot(token, state.selectedProjectId),
      ]);
      setState((currentState) => ({
        ...currentState,
        activeAction: null,
        lifecycleResult,
        runtimeSnapshot,
        selectedProject,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        activeAction: null,
        errorMessage: formatErrorMessage(error, "Unable to execute the lifecycle action."),
      }));
    }
  });

  const updateLifecycleConfiguration = useEffectEvent(
    async (configurationInput: ProjectLifecycleConfigurationInput) => {
      if (token === null || state.selectedProjectId === null) {
        return;
      }

      setState((currentState) => ({
        ...currentState,
        configurationMessage: null,
        errorMessage: null,
        isUpdatingLifecycleConfiguration: true,
      }));

      try {
        const selectedProject = await updateProjectLifecycleConfiguration(
          token,
          state.selectedProjectId,
          configurationInput,
        );
        setState((currentState) => ({
          ...currentState,
          configurationMessage: "Lifecycle configuration updated.",
          errorMessage: null,
          isUpdatingLifecycleConfiguration: false,
          lifecycleResult: null,
          projects: replaceProjectInList(currentState.projects, selectedProject),
          selectedProject,
        }));
      } catch (error) {
        setState((currentState) => ({
          ...currentState,
          errorMessage: formatErrorMessage(error, "Unable to update lifecycle configuration."),
          isUpdatingLifecycleConfiguration: false,
        }));
      }
    },
  );

  const updateSelectedProject = useEffectEvent(async (projectInput: ProjectUpdateInput) => {
    if (token === null || state.selectedProjectId === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isUpdatingProject: true,
      projectUpdateMessage: null,
    }));

    try {
      const selectedProject = await updateProject(token, state.selectedProjectId, projectInput);
      const runtimeSnapshot = await getRuntimeSnapshot(token, selectedProject.id);
      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isUpdatingProject: false,
        lifecycleResult: null,
        projectUpdateMessage: `${selectedProject.reference_name} updated.`,
        projects: replaceProjectInList(currentState.projects, selectedProject),
        runtimeSnapshot,
        selectedProject,
        selectedProjectId: selectedProject.id,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to update the project."),
        isUpdatingProject: false,
        projectUpdateMessage: null,
      }));
    }
  });

  const reloadSelectedProject = useEffectEvent(async () => {
    if (token === null || state.selectedProjectId === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      configurationMessage: null,
      errorMessage: null,
      isReloadingProject: true,
    }));

    try {
      const result = await reloadProject(token, state.selectedProjectId);
      const changedActions = result.changed_actions.join(", ");
      setState((currentState) => ({
        ...currentState,
        configurationMessage:
          result.changed_actions.length === 0
            ? "Lifecycle configuration reloaded with no mapping changes."
            : `Lifecycle configuration reloaded. Changed actions: ${changedActions}.`,
        errorMessage: null,
        isReloadingProject: false,
        lifecycleResult: null,
        projects: replaceProjectInList(currentState.projects, result.project),
        selectedProject: result.project,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to reload lifecycle configuration."),
        isReloadingProject: false,
      }));
    }
  });

  const refresh = useEffectEvent(async () => {
    if (token === null) {
      return;
    }

    await refreshProjects(token);
  });

  const visibleProjects = state.projects.filter((project) => {
    if (deferredSearchQuery.trim().length === 0) {
      return true;
    }

    const normalizedQuery = deferredSearchQuery.toLowerCase();
    return (
      project.reference_name.toLowerCase().includes(normalizedQuery) ||
      (project.description ?? "").toLowerCase().includes(normalizedQuery)
    );
  });

  return {
    activeAction: state.activeAction,
    acceptUpdatedProject,
    configurationMessage: state.configurationMessage,
    errorMessage: state.errorMessage,
    isReloadingProject: state.isReloadingProject,
    isLoadingDetail: state.isLoadingDetail,
    isLoadingProjects: state.isLoadingProjects,
    isRegisteringProject: state.isRegisteringProject,
    isUpdatingProject: state.isUpdatingProject,
    isUpdatingLifecycleConfiguration: state.isUpdatingLifecycleConfiguration,
    lifecycleResult: state.lifecycleResult,
    projects: visibleProjects,
    projectUpdateMessage: state.projectUpdateMessage,
    registrationMessage: state.registrationMessage,
    reloadSelectedProject,
    refresh,
    runLifecycleAction,
    runtimeSnapshot: state.runtimeSnapshot,
    searchQuery: state.searchQuery,
    selectProject,
    selectedProject: state.selectedProject,
    selectedProjectId: state.selectedProjectId,
    setSearchQuery,
    submitProjectRegistration,
    updateLifecycleConfiguration,
    updateSelectedProject,
  };
}
