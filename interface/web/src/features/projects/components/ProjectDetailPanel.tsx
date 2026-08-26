import "./ProjectDetailPanel.css";

import type { UserSummary } from "../../../shared/types/auth";
import type {
  CanonicalLifecycleAction,
  LifecycleExecutionSnapshot,
  ProjectSummary,
  RuntimeInspectionSnapshot,
} from "../../../shared/types/project";

type ProjectDetailPanelProps = {
  activeAction: CanonicalLifecycleAction | null;
  currentUser: UserSummary;
  errorMessage: string | null;
  isLoadingDetail: boolean;
  lifecycleResult: LifecycleExecutionSnapshot | null;
  onLogout: () => void;
  onRunLifecycleAction: (action: CanonicalLifecycleAction) => void;
  onRefreshProject: () => void;
  runtimeSnapshot: RuntimeInspectionSnapshot | null;
  selectedProject: ProjectSummary | null;
};

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
  currentUser,
  errorMessage,
  isLoadingDetail,
  lifecycleResult,
  onLogout,
  onRefreshProject,
  onRunLifecycleAction,
  runtimeSnapshot,
  selectedProject,
}: ProjectDetailPanelProps) {
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
          {(["status", "start", "stop", "restart"] as CanonicalLifecycleAction[]).map((action) => (
            <button
              className="project-detail__action"
              data-action={action}
              disabled={activeAction !== null}
              key={action}
              onClick={() => onRunLifecycleAction(action)}
              type="button"
            >
              {activeAction === action ? `Running ${action}...` : action}
            </button>
          ))}
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
        <h3 className="project-list__title">Lifecycle mappings</h3>
        <div className="project-detail__mappings">
          {selectedProject.action_mappings.map((mapping) => (
            <div className="project-detail__mapping" key={mapping.canonical_action}>
              <strong>{mapping.canonical_action}</strong> → {mapping.script_label}
              <br />
              source: {mapping.source} · configured_by_user_id: {mapping.configured_by_user_id}
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
    </section>
  );
}
