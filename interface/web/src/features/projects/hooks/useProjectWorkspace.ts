import { startTransition, useDeferredValue, useEffect, useEffectEvent, useState } from "react";

import {
  executeLifecycleAction,
  getProject,
  getRuntimeSnapshot,
  listProjects,
  registerProject,
} from "../../../shared/api/projects";
import type {
  CanonicalLifecycleAction,
  LifecycleExecutionSnapshot,
  ProjectRegistrationInput,
  ProjectSummary,
  RuntimeInspectionSnapshot,
} from "../../../shared/types/project";

type ProjectWorkspaceState = {
  activeAction: CanonicalLifecycleAction | null;
  errorMessage: string | null;
  isLoadingDetail: boolean;
  isLoadingProjects: boolean;
  isRegisteringProject: boolean;
  lifecycleResult: LifecycleExecutionSnapshot | null;
  projects: ProjectSummary[];
  registrationMessage: string | null;
  runtimeSnapshot: RuntimeInspectionSnapshot | null;
  searchQuery: string;
  selectedProject: ProjectSummary | null;
  selectedProjectId: number | null;
};

const initialState: ProjectWorkspaceState = {
  activeAction: null,
  errorMessage: null,
  isLoadingDetail: false,
  isLoadingProjects: false,
  isRegisteringProject: false,
  lifecycleResult: null,
  projects: [],
  registrationMessage: null,
  runtimeSnapshot: null,
  searchQuery: "",
  selectedProject: null,
  selectedProjectId: null,
};

function buildErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
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
        errorMessage: buildErrorMessage(error, "Unable to load the selected project."),
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
        errorMessage: buildErrorMessage(error, "Unable to load managed projects."),
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
          errorMessage: buildErrorMessage(error, "Unable to register the project."),
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
        errorMessage: buildErrorMessage(error, "Unable to execute the lifecycle action."),
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
    errorMessage: state.errorMessage,
    isLoadingDetail: state.isLoadingDetail,
    isLoadingProjects: state.isLoadingProjects,
    isRegisteringProject: state.isRegisteringProject,
    lifecycleResult: state.lifecycleResult,
    projects: visibleProjects,
    registrationMessage: state.registrationMessage,
    refresh,
    runLifecycleAction,
    runtimeSnapshot: state.runtimeSnapshot,
    searchQuery: state.searchQuery,
    selectProject,
    selectedProject: state.selectedProject,
    selectedProjectId: state.selectedProjectId,
    setSearchQuery,
    submitProjectRegistration,
  };
}
