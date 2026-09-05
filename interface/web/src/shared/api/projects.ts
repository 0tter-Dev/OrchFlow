import { requestJson } from "./client";
import type {
  CanonicalLifecycleAction,
  LifecycleExecutionSnapshot,
  ProjectLifecycleConfigurationInput,
  ProjectRegistrationInput,
  ProjectReloadResult,
  ProjectSummary,
  ProjectUnlinkResult,
  ProjectUpdateInput,
  RuntimeInspectionSnapshot,
} from "../types/project";

export function listProjects(token: string): Promise<ProjectSummary[]> {
  return requestJson<ProjectSummary[]>("/projects", { token });
}

export function registerProject(
  token: string,
  payload: ProjectRegistrationInput,
): Promise<ProjectSummary> {
  return requestJson<ProjectSummary>("/projects", {
    body: payload,
    method: "POST",
    token,
  });
}

export function getProject(token: string, projectId: number): Promise<ProjectSummary> {
  return requestJson<ProjectSummary>(`/projects/${projectId}`, { token });
}

export function updateProject(
  token: string,
  projectId: number,
  payload: ProjectUpdateInput,
): Promise<ProjectSummary> {
  return requestJson<ProjectSummary>(`/projects/${projectId}`, {
    body: payload,
    method: "PATCH",
    token,
  });
}

export function unlinkProject(token: string, projectId: number): Promise<ProjectUnlinkResult> {
  return requestJson<ProjectUnlinkResult>(`/projects/${projectId}`, {
    method: "DELETE",
    token,
  });
}

export function updateProjectLifecycleConfiguration(
  token: string,
  projectId: number,
  payload: ProjectLifecycleConfigurationInput,
): Promise<ProjectSummary> {
  return requestJson<ProjectSummary>(`/projects/${projectId}/lifecycle-configuration`, {
    body: payload,
    method: "PATCH",
    token,
  });
}

export function reloadProject(token: string, projectId: number): Promise<ProjectReloadResult> {
  return requestJson<ProjectReloadResult>(`/projects/${projectId}/reload`, {
    method: "POST",
    token,
  });
}

export function reloadProjects(
  token: string,
  projectIds: number[],
): Promise<ProjectReloadResult[]> {
  return requestJson<ProjectReloadResult[]>("/projects/reload", {
    body: { project_ids: projectIds },
    method: "POST",
    token,
  });
}

export function addProjectOwner(
  token: string,
  projectId: number,
  userId: number,
): Promise<ProjectSummary> {
  return requestJson<ProjectSummary>(`/projects/${projectId}/owners/${userId}`, {
    method: "POST",
    token,
  });
}

export function removeProjectOwner(
  token: string,
  projectId: number,
  userId: number,
): Promise<ProjectSummary> {
  return requestJson<ProjectSummary>(`/projects/${projectId}/owners/${userId}`, {
    method: "DELETE",
    token,
  });
}

export function getRuntimeSnapshot(
  token: string,
  projectId: number,
): Promise<RuntimeInspectionSnapshot> {
  return requestJson<RuntimeInspectionSnapshot>(`/projects/${projectId}/runtime`, { token });
}

export function getRuntimeSnapshots(
  token: string,
  projectIds: number[],
): Promise<RuntimeInspectionSnapshot[]> {
  return requestJson<RuntimeInspectionSnapshot[]>("/projects/runtime-inspections", {
    body: { project_ids: projectIds },
    method: "POST",
    token,
  });
}

export function executeLifecycleAction(
  token: string,
  projectId: number,
  action: CanonicalLifecycleAction,
): Promise<LifecycleExecutionSnapshot> {
  return requestJson<LifecycleExecutionSnapshot>(`/projects/${projectId}/lifecycle/${action}`, {
    method: "POST",
    token,
  });
}
