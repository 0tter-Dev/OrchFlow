import "./ProjectListPanel.css";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import * as Select from "@radix-ui/react-select";
import { getCoreRowModel, useLegacyTable } from "@tanstack/react-table/legacy";
import { z } from "zod";

import { ErrorNotice } from "../../../shared/components/ErrorNotice";
import type { UserSummary } from "../../../shared/types/auth";
import type { ProjectViewMode } from "../../../shared/types/preferences";
import type {
  CanonicalLifecycleAction,
  ProjectRegistrationInput,
  ProjectSummary,
  RuntimeInspectionSnapshot,
} from "../../../shared/types/project";

type ProjectListPanelProps = {
  currentUser: UserSummary;
  errorMessage: string | null;
  isLoading: boolean;
  isRegisteringProject: boolean;
  onPickLocalPath?: (kind: "project_root" | "lifecycle_script") => Promise<string | null>;
  onRefresh: () => void;
  onRegisterProject: (registrationInput: ProjectRegistrationInput) => void;
  onSearchQueryChange: (searchQuery: string) => void;
  onSelectProject: (projectId: number) => void;
  projectViewMode: ProjectViewMode;
  projects: ProjectSummary[];
  registrationMessage: string | null;
  runtimeSnapshotsByProjectId: Record<number, RuntimeInspectionSnapshot>;
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

type ProjectSort = "name" | "readiness" | "runtime";

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

const registrationDraftKey = "orchflow.project-registration-draft";
const registrationSchema = z.object({
  description: z.string(),
  lifecycle_script_path: z.string().trim().min(1, "Choose or enter a lifecycle script path."),
  map_restart: z.string(),
  map_start: z.string(),
  map_status: z.string(),
  map_stop: z.string(),
  project_root_path: z.string().trim().min(1, "Choose or enter a project root path."),
  reference_name: z.string().trim().min(1, "Enter a project reference name."),
});

function loadRegistrationDraft(): ProjectRegistrationFormState {
  try {
    const draft = window.localStorage.getItem(registrationDraftKey);
    return draft === null ? initialRegistrationFormState : { ...initialRegistrationFormState, ...JSON.parse(draft) };
  } catch {
    return initialRegistrationFormState;
  }
}

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
  onPickLocalPath,
  onRegisterProject,
  onSearchQueryChange,
  onSelectProject,
  projectViewMode,
  projects,
  registrationMessage,
  runtimeSnapshotsByProjectId,
  searchQuery,
  selectedProjectId,
}: ProjectListPanelProps) {
  const registrationForm = useForm<ProjectRegistrationFormState>({ defaultValues: loadRegistrationDraft() });
  const [isRegistrationOpen, setIsRegistrationOpen] = useState(false);
  const [sort, setSort] = useState<ProjectSort>("name");

  useEffect(() => {
    const subscription = registrationForm.watch((draft) => {
      window.localStorage.setItem(registrationDraftKey, JSON.stringify(draft));
    });
    return () => subscription.unsubscribe();
  }, [registrationForm]);

  async function pickPath(kind: "project_root" | "lifecycle_script") {
    const path = await onPickLocalPath?.(kind);
    if (path != null) {
      registrationForm.setValue(
        kind === "project_root" ? "project_root_path" : "lifecycle_script_path",
        path,
        { shouldDirty: true, shouldValidate: true },
      );
    }
  }

  function submitRegistration(formState: ProjectRegistrationFormState) {
    const parsed = registrationSchema.safeParse(formState);
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        registrationForm.setError(issue.path[0] as keyof ProjectRegistrationFormState, { message: issue.message });
      }
      return;
    }
    onRegisterProject({
      description: formState.description.trim() || null,
      lifecycle_script_path: formState.lifecycle_script_path.trim(),
      mappings: buildMappings(formState),
      project_root_path: formState.project_root_path.trim(),
      reference_name: formState.reference_name.trim(),
    });
  }

  const guidance = buildProjectGuidance(projects, selectedProjectId);
  const sortedProjects = [...projects].sort((left, right) => {
    if (sort === "readiness") {
      return left.lifecycle_configuration_health.localeCompare(right.lifecycle_configuration_health);
    }
    if (sort === "runtime") {
      return (runtimeSnapshotsByProjectId[left.id]?.status ?? "unknown").localeCompare(
        runtimeSnapshotsByProjectId[right.id]?.status ?? "unknown",
      );
    }
    return left.reference_name.localeCompare(right.reference_name);
  });
  const table = useLegacyTable({ columns: [], data: sortedProjects, getCoreRowModel: getCoreRowModel() });

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
        <div className="project-list__sort">
          <span>Sort by</span>
          <Select.Root onValueChange={(value) => setSort(value as ProjectSort)} value={sort}>
            <Select.Trigger aria-label="Sort projects"><Select.Value /></Select.Trigger>
            <Select.Portal><Select.Content className="project-list__select-content"><Select.Viewport>
              <Select.Item value="name"><Select.ItemText>Name</Select.ItemText></Select.Item>
              <Select.Item value="readiness"><Select.ItemText>Lifecycle readiness</Select.ItemText></Select.Item>
              <Select.Item value="runtime"><Select.ItemText>Runtime status</Select.ItemText></Select.Item>
            </Select.Viewport></Select.Content></Select.Portal>
          </Select.Root>
        </div>
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

      <button
        className="project-list__button"
        onClick={() => setIsRegistrationOpen((isOpen) => !isOpen)}
        type="button"
      >
        {isRegistrationOpen ? "Close registration" : "Register project"}
      </button>

      {isRegistrationOpen ? <form className="project-list__registration" noValidate onSubmit={registrationForm.handleSubmit(submitRegistration)}>
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
            aria-invalid={registrationForm.formState.errors.reference_name !== undefined}
            {...registrationForm.register("reference_name")}
            placeholder="orchflow-local-api"
          />
          {registrationForm.formState.errors.reference_name ? <span role="alert">{registrationForm.formState.errors.reference_name.message}</span> : null}
        </label>

        <label className="project-list__field">
          <span>Description</span>
          <textarea
            {...registrationForm.register("description")}
            placeholder="Local API project managed by an existing control.bat script"
            rows={3}
          />
        </label>

        <label className="project-list__field">
          <span>Project root path</span>
          <div className="project-list__path-input"><input aria-invalid={registrationForm.formState.errors.project_root_path !== undefined} {...registrationForm.register("project_root_path")} placeholder="E:\\Projects\\local-api" /><button onClick={() => void pickPath("project_root")} type="button">Browse</button></div>
          {registrationForm.formState.errors.project_root_path ? <span role="alert">{registrationForm.formState.errors.project_root_path.message}</span> : null}
        </label>

        <label className="project-list__field">
          <span>Lifecycle script path</span>
          <div className="project-list__path-input"><input aria-invalid={registrationForm.formState.errors.lifecycle_script_path !== undefined} {...registrationForm.register("lifecycle_script_path")} placeholder="E:\\Projects\\local-api\\control.bat" /><button onClick={() => void pickPath("lifecycle_script")} type="button">Browse</button></div>
          {registrationForm.formState.errors.lifecycle_script_path ? <span role="alert">{registrationForm.formState.errors.lifecycle_script_path.message}</span> : null}
        </label>

        <div className="project-list__mapping-grid" aria-label="Lifecycle action mappings">
          <label className="project-list__field">
            <span>Status mapping</span>
            <input
              {...registrationForm.register("map_status")}
              placeholder="STATUS"
            />
          </label>
          <label className="project-list__field">
            <span>Start mapping</span>
            <input
              {...registrationForm.register("map_start")}
              placeholder="INICIAR"
            />
          </label>
          <label className="project-list__field">
            <span>Stop mapping</span>
            <input
              {...registrationForm.register("map_stop")}
              placeholder="PARAR"
            />
          </label>
          <label className="project-list__field">
            <span>Restart mapping</span>
            <input
              {...registrationForm.register("map_restart")}
              placeholder="REINICIAR"
            />
          </label>
        </div>
      </form> : null}

      {sortedProjects.length === 0 ? (
        <div className="project-list__empty">
          No managed project is visible here yet. Register an existing project with a compatible
          lifecycle `.bat` script to start operating it from this workspace.
        </div>
      ) : (
        <div className="project-list__items" data-view={projectViewMode}>
          {table.getRowModel().rows.map(({ original: project }) => {
            const runtimeSnapshot = runtimeSnapshotsByProjectId[project.id];
            return (
              <button
                className="project-list__item"
                data-selected={selectedProjectId === project.id}
                key={project.id}
                onClick={() => onSelectProject(project.id)}
                type="button"
              >
                <strong>{project.reference_name}</strong>
                <span className="project-list__badges">
                  <span
                    className="project-list__health"
                    data-health={project.lifecycle_configuration_health}
                  >
                    {project.lifecycle_configuration_health}
                  </span>
                  <span
                    className="project-list__runtime-status"
                    data-status={runtimeSnapshot?.status ?? "loading"}
                  >
                    {runtimeSnapshot?.status ?? "runtime loading"}
                  </span>
                </span>
                <span className="project-list__description">
                  {project.description ?? "No description registered for this project yet."}
                </span>
                <span className="project-list__owners">
                  Owners: {project.owner_user_ids.join(", ")}
                </span>
                <span className="project-list__runtime-meta">
                  {runtimeSnapshot?.known_port
                    ? `Port ${runtimeSnapshot.known_port}`
                    : "No runtime port"}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </aside>
  );
}
