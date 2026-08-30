import "./ProjectDetailPanel.css";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import type { UserSummary } from "../../../shared/types/auth";
import type {
  CanonicalLifecycleAction,
  LifecycleExecutionSnapshot,
  ProjectLifecycleConfigurationInput,
  ProjectSummary,
  RuntimeInspectionSnapshot,
} from "../../../shared/types/project";

const lifecycleActions: CanonicalLifecycleAction[] = ["status", "start", "stop", "restart"];

type ProjectDetailPanelProps = {
  activeAction: CanonicalLifecycleAction | null;
  configurationMessage: string | null;
  currentUser: UserSummary;
  errorMessage: string | null;
  isLoadingDetail: boolean;
  isReloadingProject: boolean;
  isUpdatingLifecycleConfiguration: boolean;
  lifecycleResult: LifecycleExecutionSnapshot | null;
  onLogout: () => void;
  onReloadProject: () => void;
  onRunLifecycleAction: (action: CanonicalLifecycleAction) => void;
  onRefreshProject: () => void;
  onUpdateLifecycleConfiguration: (configurationInput: ProjectLifecycleConfigurationInput) => void;
  runtimeSnapshot: RuntimeInspectionSnapshot | null;
  selectedProject: ProjectSummary | null;
};

type MappingFormState = Record<
  CanonicalLifecycleAction,
  {
    isUnconfigured: boolean;
    scriptLabel: string;
  }
>;

function buildMappingFormState(project: ProjectSummary): MappingFormState {
  return lifecycleActions.reduce((formState, action) => {
    const configuration = project.lifecycle_function_configurations.find(
      (item) => item.canonical_action === action,
    );
    return {
      ...formState,
      [action]: {
        isUnconfigured: configuration?.state === "unconfigured",
        scriptLabel: configuration?.script_label ?? "",
      },
    };
  }, {} as MappingFormState);
}

function formatUptime(uptimeSeconds: number | null): string {
  if (uptimeSeconds === null) {
    return "Unavailable";
  }

  const roundedSeconds = Math.max(0, Math.floor(uptimeSeconds));
  const hours = Math.floor(roundedSeconds / 3600);
  const minutes = Math.floor((roundedSeconds % 3600) / 60);
  const seconds = roundedSeconds % 60;
  return `${hours}h ${minutes}m ${seconds}s`;
}

function formatMemory(memoryBytes: number | null): string {
  if (memoryBytes === null) {
    return "Unavailable";
  }

  const megabytes = memoryBytes / (1024 * 1024);
  return `${megabytes.toFixed(1)} MB`;
}

function formatReachability(applicationReachable: boolean | null | undefined): string {
  if (applicationReachable === undefined || applicationReachable === null) {
    return "Not checked";
  }
  return applicationReachable ? "Reachable" : "Not reachable";
}

function formatTimestamp(value: string | null | undefined): string {
  if (value === undefined || value === null) {
    return "Unavailable";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export function ProjectDetailPanel({
  activeAction,
  configurationMessage,
  currentUser,
  errorMessage,
  isLoadingDetail,
  isReloadingProject,
  isUpdatingLifecycleConfiguration,
  lifecycleResult,
  onLogout,
  onReloadProject,
  onRefreshProject,
  onRunLifecycleAction,
  onUpdateLifecycleConfiguration,
  runtimeSnapshot,
  selectedProject,
}: ProjectDetailPanelProps) {
  const [isMappingPanelOpen, setIsMappingPanelOpen] = useState(false);
  const [mappingFormState, setMappingFormState] = useState<MappingFormState | null>(null);

  useEffect(() => {
    if (selectedProject === null) {
      setMappingFormState(null);
      setIsMappingPanelOpen(false);
      return;
    }
    setMappingFormState(buildMappingFormState(selectedProject));
  }, [selectedProject]);

  if (selectedProject === null) {
    return (
      <section className="project-detail">
        <div className="project-detail__placeholder">
          Sign in and choose a project from the registry panel to inspect lifecycle metadata,
          runtime information, and the first web lifecycle actions.
        </div>
      </section>
    );
  }

  const configurationByAction = new Map(
    selectedProject.lifecycle_function_configurations.map((configuration) => [
      configuration.canonical_action,
      configuration,
    ]),
  );
  const blockedProject = selectedProject.lifecycle_configuration_health === "blocked";
  const partialProject = selectedProject.lifecycle_configuration_health === "partial";

  function updateMappingLabel(action: CanonicalLifecycleAction, scriptLabel: string) {
    setMappingFormState((currentState) =>
      currentState === null
        ? currentState
        : {
            ...currentState,
            [action]: {
              isUnconfigured: false,
              scriptLabel,
            },
          },
    );
  }

  function updateMappingUnconfigured(
    action: CanonicalLifecycleAction,
    isUnconfigured: boolean,
  ) {
    setMappingFormState((currentState) =>
      currentState === null
        ? currentState
        : {
            ...currentState,
            [action]: {
              ...currentState[action],
              isUnconfigured,
              scriptLabel: isUnconfigured ? "" : currentState[action].scriptLabel,
            },
          },
    );
  }

  function submitLifecycleConfiguration(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (mappingFormState === null) {
      return;
    }

    const mappings = lifecycleActions
      .map((action) => ({
        canonical_action: action,
        script_label: mappingFormState[action].scriptLabel.trim(),
        source: "user_defined" as const,
      }))
      .filter(
        (mapping) =>
          mapping.script_label.length > 0 &&
          !mappingFormState[mapping.canonical_action].isUnconfigured,
      );
    const unconfigured_actions = lifecycleActions.filter(
      (action) => mappingFormState[action].isUnconfigured,
    );

    onUpdateLifecycleConfiguration({ mappings, unconfigured_actions });
    setIsMappingPanelOpen(false);
  }

  return (
    <section className="project-detail">
      <header className="project-detail__header">
        <div>
          <span className="project-detail__eyebrow">Operator workspace</span>
          <h2 className="project-detail__title">{selectedProject.reference_name}</h2>
          <p className="project-detail__copy">
            {selectedProject.description ?? "No description registered for this project yet."}
          </p>
          <p className="project-detail__copy">
            Signed in as <strong>{currentUser.username}</strong> ({currentUser.role})
          </p>
        </div>

        <button className="project-detail__logout" onClick={onLogout} type="button">
          End session
        </button>
      </header>

      {errorMessage !== null ? <div className="project-detail__error">{errorMessage}</div> : null}
      {configurationMessage !== null ? (
        <div className="project-detail__success">{configurationMessage}</div>
      ) : null}

      <section
        className="project-detail__configuration-banner"
        data-health={selectedProject.lifecycle_configuration_health}
      >
        <div>
          <span className="project-detail__label">Lifecycle configuration</span>
          <strong>{selectedProject.lifecycle_configuration_health}</strong>
          <p>
            {blockedProject
              ? "No lifecycle function is configured for execution."
              : partialProject
                ? "Some ideal lifecycle functions still need mapping or confirmation."
                : "All ideal lifecycle functions are configured."}
          </p>
        </div>
        <div className="project-detail__configuration-actions">
          <button
            className="project-detail__secondary-action"
            disabled={isReloadingProject}
            onClick={onReloadProject}
            type="button"
          >
            {isReloadingProject ? "Reloading..." : "Reload"}
          </button>
          <button
            className="project-detail__secondary-action"
            onClick={() => setIsMappingPanelOpen(true)}
            type="button"
          >
            Configure
          </button>
          <button className="project-detail__secondary-action" disabled type="button">
            AI improvement
          </button>
        </div>
      </section>

      <div className="project-detail__grid">
        <article className="project-detail__card">
          <span className="project-detail__label">Project root</span>
          <p className="project-detail__value">{selectedProject.project_root_path}</p>
        </article>
        <article className="project-detail__card">
          <span className="project-detail__label">Lifecycle script</span>
          <p className="project-detail__value">{selectedProject.lifecycle_script_path}</p>
        </article>
        <article className="project-detail__card">
          <span className="project-detail__label">Owners</span>
          <p className="project-detail__value">{selectedProject.owner_user_ids.join(", ")}</p>
        </article>
        <article className="project-detail__card">
          <span className="project-detail__label">Created by</span>
          <p className="project-detail__value">{selectedProject.created_by_user_id}</p>
        </article>
      </div>

      <section>
        <div className="project-list__title-row">
          <h3 className="project-list__title">Runtime snapshot</h3>
          <button className="project-list__button" onClick={onRefreshProject} type="button">
            {isLoadingDetail ? "Refreshing..." : "Refresh snapshot"}
          </button>
        </div>
        <div className="project-detail__runtime">
          <article className="project-detail__runtime-card">
            <span className="project-detail__label">Runtime status</span>
            <strong data-status={runtimeSnapshot?.status ?? "unknown"}>
              {runtimeSnapshot?.status ?? "Loading..."}
            </strong>
          </article>
          <article className="project-detail__runtime-card">
            <span className="project-detail__label">Known port</span>
            <strong>{runtimeSnapshot?.known_port ?? "Unavailable"}</strong>
          </article>
          <article className="project-detail__runtime-card">
            <span className="project-detail__label">Application URL</span>
            <strong>{runtimeSnapshot?.application_url ?? "Unavailable"}</strong>
          </article>
          <article className="project-detail__runtime-card">
            <span className="project-detail__label">URL reachability</span>
            <strong>{formatReachability(runtimeSnapshot?.application_reachable)}</strong>
          </article>
          <article className="project-detail__runtime-card">
            <span className="project-detail__label">Uptime</span>
            <strong>{formatUptime(runtimeSnapshot?.uptime_seconds ?? null)}</strong>
          </article>
          <article className="project-detail__runtime-card">
            <span className="project-detail__label">Inspected at</span>
            <strong>{formatTimestamp(runtimeSnapshot?.inspected_at)}</strong>
          </article>
          <article className="project-detail__runtime-card project-detail__runtime-card--wide">
            <span className="project-detail__label">Runtime explanation</span>
            <strong>{runtimeSnapshot?.status_reason ?? "Waiting for runtime inspection."}</strong>
          </article>
        </div>
      </section>

      <section>
        <h3 className="project-list__title">Lifecycle actions</h3>
        <div className="project-detail__actions">
          {lifecycleActions.map((action) => {
            const configuration = configurationByAction.get(action);
            const isConfigured = configuration?.state === "configured";
            return (
              <button
                className="project-detail__action"
                data-action={action}
                data-state={configuration?.state ?? "undefined"}
                disabled={activeAction !== null || !isConfigured}
                key={action}
                onClick={() => onRunLifecycleAction(action)}
                type="button"
              >
                <span>{activeAction === action ? `Running ${action}...` : action}</span>
                <small>{configuration?.state ?? "undefined"}</small>
              </button>
            );
          })}
        </div>
      </section>

      {lifecycleResult !== null ? (
        <section>
          <h3 className="project-list__title">Last lifecycle result</h3>
          <pre className="project-detail__console">{[
            `action: ${lifecycleResult.canonical_action}`,
            `command_identifier: ${lifecycleResult.command_identifier}`,
            `exit_code: ${lifecycleResult.exit_code}`,
            `succeeded: ${String(lifecycleResult.succeeded)}`,
            `runtime_status: ${lifecycleResult.runtime_status ?? "unavailable"}`,
            "",
            "[stdout]",
            lifecycleResult.stdout || "(empty)",
            "",
            "[stderr]",
            lifecycleResult.stderr || "(empty)",
          ].join("\n")}</pre>
        </section>
      ) : null}

      <section>
        <div className="project-list__title-row">
          <h3 className="project-list__title">Lifecycle mappings</h3>
          <button
            className="project-list__button"
            onClick={() => setIsMappingPanelOpen(true)}
            type="button"
          >
            Configure mappings
          </button>
        </div>
        <div className="project-detail__mappings">
          {selectedProject.lifecycle_function_configurations.map((configuration) => (
            <div
              className="project-detail__mapping"
              data-state={configuration.state}
              key={configuration.canonical_action}
            >
              <strong>{configuration.canonical_action}</strong> {configuration.state}
              <br />
              preferred: {configuration.preferred_script_identifier}
              {configuration.script_label !== null ? (
                <>
                  <br />
                  mapped to: {configuration.script_label}
                </>
              ) : null}
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3 className="project-list__title">Observed processes</h3>
        <div className="project-detail__processes">
          {runtimeSnapshot?.process_snapshots.length ? (
            runtimeSnapshot.process_snapshots.map((processSnapshot) => (
              <div className="project-detail__process" key={processSnapshot.pid}>
                <strong>
                  {processSnapshot.name} (PID {processSnapshot.pid})
                </strong>
                <br />
                cpu: {processSnapshot.cpu_seconds ?? "Unavailable"}s · memory:{" "}
                {formatMemory(processSnapshot.memory_bytes)}
                <br />
                started_at: {processSnapshot.started_at ?? "Unavailable"}
              </div>
            ))
          ) : (
            <div className="project-detail__placeholder">
              No process snapshot is currently associated with this project runtime.
            </div>
          )}
        </div>
      </section>

      {isMappingPanelOpen && mappingFormState !== null ? (
        <div className="project-detail__modal-backdrop" role="presentation">
          <section
            aria-labelledby="lifecycle-configuration-title"
            className="project-detail__modal"
            role="dialog"
          >
            <form onSubmit={submitLifecycleConfiguration}>
              <div className="project-detail__modal-header">
                <h3 id="lifecycle-configuration-title">Lifecycle configuration</h3>
                <button
                  className="project-detail__secondary-action"
                  onClick={() => setIsMappingPanelOpen(false)}
                  type="button"
                >
                  Close
                </button>
              </div>

              <div className="project-detail__configuration-form">
                {lifecycleActions.map((action) => {
                  const configuration = configurationByAction.get(action);
                  return (
                    <fieldset className="project-detail__configuration-field" key={action}>
                      <legend>{action}</legend>
                      <label>
                        <span>Script label</span>
                        <input
                          disabled={mappingFormState[action].isUnconfigured}
                          onChange={(event) => updateMappingLabel(action, event.target.value)}
                          placeholder={configuration?.preferred_script_identifier ?? action.toUpperCase()}
                          value={mappingFormState[action].scriptLabel}
                        />
                      </label>
                      <label className="project-detail__checkbox">
                        <input
                          checked={mappingFormState[action].isUnconfigured}
                          onChange={(event) =>
                            updateMappingUnconfigured(action, event.target.checked)
                          }
                          type="checkbox"
                        />
                        <span>Leave unconfigured</span>
                      </label>
                    </fieldset>
                  );
                })}
              </div>

              <div className="project-detail__modal-actions">
                <button
                  className="project-detail__secondary-action"
                  onClick={() => setIsMappingPanelOpen(false)}
                  type="button"
                >
                  Cancel
                </button>
                <button
                  className="project-detail__primary-action"
                  disabled={isUpdatingLifecycleConfiguration}
                  type="submit"
                >
                  {isUpdatingLifecycleConfiguration ? "Saving..." : "Save configuration"}
                </button>
              </div>
            </form>
          </section>
        </div>
      ) : null}
    </section>
  );
}
