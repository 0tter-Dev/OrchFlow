import "./ProjectListPanel.css";

import { useState } from "react";
import type { FormEvent } from "react";

import { ErrorNotice } from "../../../shared/components/ErrorNotice";
import type { UserSummary } from "../../../shared/types/auth";
import type { ProjectViewMode } from "../../../shared/types/preferences";
import type {
  CanonicalLifecycleAction,
  ProjectRegistrationInput,
  ProjectSummary,
} from "../../../shared/types/project";

type ProjectListPanelProps = {
  currentUser: UserSummary;
  errorMessage: string | null;
  isLoading: boolean;
  isRegisteringProject: boolean;
  onRefresh: () => void;
  onRegisterProject: (registrationInput: ProjectRegistrationInput) => void;
  onSearchQueryChange: (searchQuery: string) => void;
  onSelectProject: (projectId: number) => void;
  projectViewMode: ProjectViewMode;
  projects: ProjectSummary[];
  registrationMessage: string | null;
  searchQuery: string;
  selectedProjectId: number | null;
};

type ProjectRegistrationFormState = {
  description: string;
  lifecycle_script_path: string;
  map_restart: string;
  map_start: string;
  map_status: string;
  map_stop: string;
  project_root_path: string;
  reference_name: string;
};

type ProjectGuidance = {
  detail: string;
  tone: "attention" | "blocked" | "ready";
  title: string;
};

const initialRegistrationFormState: ProjectRegistrationFormState = {
  description: "",
  lifecycle_script_path: "",
  map_restart: "",
  map_start: "",
  map_status: "",
  map_stop: "",
  project_root_path: "",
  reference_name: "",
};

function buildMappings(formState: ProjectRegistrationFormState) {
  const mappingValues: [CanonicalLifecycleAction, string][] = [
    ["status", formState.map_status],
    ["start", formState.map_start],
    ["stop", formState.map_stop],
    ["restart", formState.map_restart],
  ];

  return mappingValues
    .map(([canonical_action, script_label]) => ({
      canonical_action,
      script_label: script_label.trim(),
      source: "user_defined" as const,
    }))
    .filter((mapping) => mapping.script_label.length > 0);
}

function buildProjectGuidance(
  projects: ProjectSummary[],
  selectedProjectId: number | null,
): ProjectGuidance {
  if (projects.length === 0) {
    return {
      detail:
        "Connect an existing lifecycle .bat script so OrchFlow can import its first project.",
      title: "Register the first managed project",
      tone: "attention",
    };
  }

  const selectedProject =
    selectedProjectId === null
      ? null
      : projects.find((project) => project.id === selectedProjectId) ?? null;

  if (selectedProject === null) {
    return {
      detail:
        "Choose one visible project to open details, runtime diagnostics, lifecycle controls, and readiness guidance.",
      title: "Select a project to continue",
      tone: "attention",
    };
  }

  if (selectedProject.lifecycle_configuration_health === "blocked") {
    return {
      detail:
        "Open mappings for the selected project before running lifecycle actions.",
      title: "Selected project is blocked",
      tone: "blocked",
    };
  }

  if (selectedProject.lifecycle_configuration_health === "partial") {
    return {
      detail:
        "Configured actions remain usable while missing lifecycle functions wait for manual mapping or AI-assisted review.",
      title: "Selected project needs readiness review",
      tone: "attention",
    };
  }

  return {
    detail:
      "Lifecycle mappings are complete; use the detail panel to inspect runtime state or run actions.",
    title: "Selected project is ready",
    tone: "ready",
  };
}

export function ProjectListPanel({
  currentUser,
  errorMessage,
  isLoading,
  isRegisteringProject,
  onRefresh,
  onRegisterProject,
  onSearchQueryChange,
  onSelectProject,
  projectViewMode,
  projects,
  registrationMessage,
  searchQuery,
  selectedProjectId,
}: ProjectListPanelProps) {
  const [formState, setFormState] = useState<ProjectRegistrationFormState>(
    initialRegistrationFormState,
  );

  function updateFormField(field: keyof ProjectRegistrationFormState, value: string) {
    setFormState((currentState) => ({
      ...currentState,
      [field]: value,
    }));
  }

  function submitRegistration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    onRegisterProject({
      description: formState.description.trim() || null,
      lifecycle_script_path: formState.lifecycle_script_path.trim(),
      mappings: buildMappings(formState),
      project_root_path: formState.project_root_path.trim(),
      reference_name: formState.reference_name.trim(),
    });
  }

  const guidance = buildProjectGuidance(projects, selectedProjectId);

  return (
    <aside className="project-list">
      <header className="project-list__header">
        <span className="project-list__eyebrow">Managed projects</span>
        <div className="project-list__title-row">
          <h2 className="project-list__title">Visible to {currentUser.username}</h2>
          <button className="project-list__button" onClick={onRefresh} type="button">
            Refresh
          </button>
        </div>
        <input
          className="project-list__search"
          onChange={(event) => onSearchQueryChange(event.target.value)}
          placeholder="Filter by name or description"
          value={searchQuery}
        />
        <p className="project-list__status">
          {isLoading ? "Loading project registry..." : `${projects.length} project(s) visible`}
        </p>
      </header>

      <section
        className="project-list__guidance"
        data-tone={guidance.tone}
      >
        <strong>{guidance.title}</strong>
        <span>{guidance.detail}</span>
      </section>

      {errorMessage !== null ? (
        <ErrorNotice
          className="project-list__error"
          message={errorMessage}
          title="Project registry needs attention"
        />
      ) : null}
      {registrationMessage !== null ? (
        <div className="project-list__success">{registrationMessage}</div>
      ) : null}

      <form className="project-list__registration" onSubmit={submitRegistration}>
        <div className="project-list__registration-header">
          <h3 className="project-list__registration-title">Register existing project</h3>
          <button
            className="project-list__button"
            disabled={isRegisteringProject}
            type="submit"
          >
            {isRegisteringProject ? "Registering..." : "Register"}
          </button>
        </div>

        <label className="project-list__field">
          <span>Name</span>
          <input
            required
            onChange={(event) => updateFormField("reference_name", event.target.value)}
            placeholder="orchflow-local-api"
            value={formState.reference_name}
          />
        </label>

        <label className="project-list__field">
          <span>Description</span>
          <textarea
            onChange={(event) => updateFormField("description", event.target.value)}
            placeholder="Local API project managed by an existing control.bat script"
            rows={3}
            value={formState.description}
          />
        </label>

        <label className="project-list__field">
          <span>Project root path</span>
          <input
            required
            onChange={(event) => updateFormField("project_root_path", event.target.value)}
            placeholder="E:\\Projects\\local-api"
            value={formState.project_root_path}
          />
        </label>

        <label className="project-list__field">
          <span>Lifecycle script path</span>
          <input
            required
            onChange={(event) => updateFormField("lifecycle_script_path", event.target.value)}
            placeholder="E:\\Projects\\local-api\\control.bat"
            value={formState.lifecycle_script_path}
          />
        </label>

        <div className="project-list__mapping-grid" aria-label="Lifecycle action mappings">
          <label className="project-list__field">
            <span>Status mapping</span>
            <input
              onChange={(event) => updateFormField("map_status", event.target.value)}
              placeholder="STATUS"
              value={formState.map_status}
            />
          </label>
          <label className="project-list__field">
            <span>Start mapping</span>
            <input
              onChange={(event) => updateFormField("map_start", event.target.value)}
              placeholder="INICIAR"
              value={formState.map_start}
            />
          </label>
          <label className="project-list__field">
            <span>Stop mapping</span>
            <input
              onChange={(event) => updateFormField("map_stop", event.target.value)}
              placeholder="PARAR"
              value={formState.map_stop}
            />
          </label>
          <label className="project-list__field">
            <span>Restart mapping</span>
            <input
              onChange={(event) => updateFormField("map_restart", event.target.value)}
              placeholder="REINICIAR"
              value={formState.map_restart}
            />
          </label>
        </div>
      </form>

      {projects.length === 0 ? (
        <div className="project-list__empty">
          No managed project is visible here yet. Register an existing project with a compatible
          lifecycle `.bat` script to start operating it from this workspace.
        </div>
      ) : (
        <div className="project-list__items" data-view={projectViewMode}>
          {projects.map((project) => (
            <button
              className="project-list__item"
              data-selected={selectedProjectId === project.id}
              key={project.id}
              onClick={() => onSelectProject(project.id)}
              type="button"
            >
              <strong>{project.reference_name}</strong>
              <span
                className="project-list__health"
                data-health={project.lifecycle_configuration_health}
              >
                {project.lifecycle_configuration_health}
              </span>
              <span className="project-list__description">
                {project.description ?? "No description registered for this project yet."}
              </span>
              <span className="project-list__owners">
                Owners: {project.owner_user_ids.join(", ")}
              </span>
            </button>
          ))}
        </div>
      )}
    </aside>
  );
}
