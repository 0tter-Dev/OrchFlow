import "./ProjectListPanel.css";

import type { UserSummary } from "../../../shared/types/auth";
import type { ProjectSummary } from "../../../shared/types/project";

type ProjectListPanelProps = {
  currentUser: UserSummary;
  errorMessage: string | null;
  isLoading: boolean;
  onRefresh: () => void;
  onSearchQueryChange: (searchQuery: string) => void;
  onSelectProject: (projectId: number) => void;
  projects: ProjectSummary[];
  searchQuery: string;
  selectedProjectId: number | null;
};

export function ProjectListPanel({
  currentUser,
  errorMessage,
  isLoading,
  onRefresh,
  onSearchQueryChange,
  onSelectProject,
  projects,
  searchQuery,
  selectedProjectId,
}: ProjectListPanelProps) {
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

      {errorMessage !== null ? <div className="project-list__error">{errorMessage}</div> : null}

      {projects.length === 0 ? (
        <div className="project-list__empty">
          No managed project is visible here yet. Use the current CLI or API surface to register a
          project first, then refresh this list.
        </div>
      ) : (
        <div className="project-list__items">
          {projects.map((project) => (
            <button
              className="project-list__item"
              data-selected={selectedProjectId === project.id}
              key={project.id}
              onClick={() => onSelectProject(project.id)}
              type="button"
            >
              <strong>{project.reference_name}</strong>
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
