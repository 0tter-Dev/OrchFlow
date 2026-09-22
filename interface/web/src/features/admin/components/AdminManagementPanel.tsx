import "./AdminManagementPanel.css";

import { ErrorNotice } from "../../../shared/components/ErrorNotice";
import { useTranslation } from "react-i18next";
import "../../../app/i18n";
import type { UserRole, UserSummary } from "../../../shared/types/auth";
import type { ProjectSummary } from "../../../shared/types/project";

type AdminManagementPanelProps = {
  canManage: boolean;
  currentUser: UserSummary;
  errorMessage: string | null;
  isLoading: boolean;
  isMutating: boolean;
  onAddOwner: (project: ProjectSummary | null, userId: number, onProjectUpdated: () => void) => void;
  onChangeUserActivation: (userId: number, isActive: boolean) => void;
  onChangeUserRole: (userId: number, role: UserRole) => void;
  onRefreshUsers: () => void;
  onRemoveOwner: (
    project: ProjectSummary | null,
    userId: number,
    onProjectUpdated: () => void,
  ) => void;
  onRefreshProject: () => void;
  selectedProject: ProjectSummary | null;
  successMessage: string | null;
  users: UserSummary[];
};

export function AdminManagementPanel({
  canManage,
  currentUser,
  errorMessage,
  isLoading,
  isMutating,
  onAddOwner,
  onChangeUserActivation,
  onChangeUserRole,
  onRefreshProject,
  onRefreshUsers,
  onRemoveOwner,
  selectedProject,
  successMessage,
  users,
}: AdminManagementPanelProps) {
  const { t } = useTranslation();
  const availableOwnerCandidates = users.filter(
    (user) => selectedProject?.owner_user_ids.includes(user.id) !== true && user.is_active,
  );

  return (
    <section className="admin-panel">
      <header className="admin-panel__header">
        <div>
          <span className="admin-panel__eyebrow">{t("workspace.adminManagement")}</span>
          <h2 className="admin-panel__title">{t("workspace.usersAndOwnership")}</h2>
        </div>
        <button
          className="admin-panel__button"
          disabled={!canManage || isLoading}
          onClick={onRefreshUsers}
          type="button"
        >
          {isLoading ? t("workspace.loading") : t("workspace.refreshUsers")}
        </button>
      </header>

      {!canManage ? (
        <div className="admin-panel__empty">{t("workspace.adminRequiredManagement")}</div>
      ) : null}

      {errorMessage !== null ? (
        <ErrorNotice
          className="admin-panel__error"
          message={errorMessage}
          title={t("workspace.adminActionAttention")}
        />
      ) : null}
      {successMessage !== null ? (
        <div className="admin-panel__success">{successMessage}</div>
      ) : null}

      {canManage ? (
        <>
          <div className="admin-panel__users">
            {users.map((user) => (
              <article className="admin-panel__user" key={user.id}>
                <div>
                  <strong>{user.username}</strong>
                  <span>
                    id: {user.id} · {user.is_active ? t("workspace.active") : t("workspace.inactive")}
                  </span>
                </div>
                <div className="admin-panel__actions">
                  <select
                    aria-label={t("workspace.roleFor", { username: user.username })}
                    disabled={isMutating}
                    onChange={(event) =>
                      onChangeUserRole(user.id, event.target.value as UserRole)
                    }
                    value={user.role}
                  >
                    <option value="admin">admin</option>
                    <option value="member">member</option>
                  </select>
                  <button
                    className="admin-panel__button"
                    disabled={isMutating || user.id === currentUser.id}
                    onClick={() => onChangeUserActivation(user.id, !user.is_active)}
                    type="button"
                  >
                    {user.is_active ? t("workspace.deactivate") : t("workspace.activate")}
                  </button>
                </div>
              </article>
            ))}
          </div>

          <section className="admin-panel__ownership">
            <h3 className="admin-panel__subtitle">{t("workspace.selectedProjectOwners")}</h3>
            {selectedProject === null ? (
              <div className="admin-panel__empty">{t("workspace.selectProjectOwners")}</div>
            ) : (
              <>
                <div className="admin-panel__owner-list">
                  {selectedProject.owner_user_ids.map((ownerId) => (
                    <div className="admin-panel__owner" key={ownerId}>
                      <span>{t("workspace.user")} {ownerId}</span>
                      <button
                        className="admin-panel__button"
                        disabled={isMutating || selectedProject.owner_user_ids.length <= 1}
                        onClick={() => onRemoveOwner(selectedProject, ownerId, onRefreshProject)}
                        type="button"
                      >
                        {t("workspace.remove")}
                      </button>
                    </div>
                  ))}
                </div>
                {availableOwnerCandidates.length > 0 ? (
                  <div className="admin-panel__owner-actions">
                    {availableOwnerCandidates.map((user) => (
                      <button
                        className="admin-panel__button"
                        disabled={isMutating}
                        key={user.id}
                        onClick={() => onAddOwner(selectedProject, user.id, onRefreshProject)}
                        type="button"
                      >
                        {t("workspace.add", { username: user.username })}
                      </button>
                    ))}
                  </div>
                ) : null}
              </>
            )}
          </section>
        </>
      ) : null}
    </section>
  );
}
