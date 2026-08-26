import { requestJson } from "./client";
import type {
  CanonicalLifecycleAction,
  LifecycleExecutionSnapshot,
  ProjectRegistrationInput,
  ProjectSummary,
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

export function getRuntimeSnapshot(
  token: string,
  projectId: number,
): Promise<RuntimeInspectionSnapshot> {
  return requestJson<RuntimeInspectionSnapshot>(`/projects/${projectId}/runtime`, { token });
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
