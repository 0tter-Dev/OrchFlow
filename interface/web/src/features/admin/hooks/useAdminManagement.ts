import { useEffect, useEffectEvent, useState } from "react";

import { listUsers, updateUser } from "../../../shared/api/auth";
import { formatErrorMessage } from "../../../shared/api/errors";
import { addProjectOwner, removeProjectOwner } from "../../../shared/api/projects";
import type { UserRole, UserSummary } from "../../../shared/types/auth";
import type { ProjectSummary } from "../../../shared/types/project";

type AdminManagementState = {
  errorMessage: string | null;
  isLoading: boolean;
  isMutating: boolean;
  successMessage: string | null;
  users: UserSummary[];
};

const initialState: AdminManagementState = {
  errorMessage: null,
  isLoading: false,
  isMutating: false,
  successMessage: null,
  users: [],
};

export function useAdminManagement(token: string | null, currentUser: UserSummary | null) {
  const [state, setState] = useState<AdminManagementState>(initialState);
  const canManage = token !== null && currentUser?.role === "admin";

  const refreshUsers = useEffectEvent(async () => {
    if (!canManage || token === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoading: true,
    }));

    try {
      const users = await listUsers(token);
      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isLoading: false,
        users,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to load users."),
        isLoading: false,
      }));
    }
  });

  useEffect(() => {
    if (!canManage) {
      setState(initialState);
      return;
    }

    void refreshUsers();
  }, [canManage, refreshUsers]);

  const changeUserRole = useEffectEvent(async (userId: number, role: UserRole) => {
    if (!canManage || token === null) {
      return;
    }

    await runMutation(async () => {
      const user = await updateUser(token, userId, { role });
      return `${user.username} role updated to ${user.role}.`;
    });
    await refreshUsers();
  });

  const changeUserActivation = useEffectEvent(async (userId: number, isActive: boolean) => {
    if (!canManage || token === null) {
      return;
    }

    await runMutation(async () => {
      const user = await updateUser(token, userId, { is_active: isActive });
      return `${user.username} is now ${user.is_active ? "active" : "inactive"}.`;
    });
    await refreshUsers();
  });

  const addOwner = useEffectEvent(
    async (project: ProjectSummary | null, userId: number, onProjectUpdated: () => void) => {
      if (!canManage || token === null || project === null) {
        return;
      }

      await runMutation(async () => {
        await addProjectOwner(token, project.id, userId);
        return `User ${userId} added as owner of ${project.reference_name}.`;
      });
      onProjectUpdated();
    },
  );

  const removeOwner = useEffectEvent(
    async (project: ProjectSummary | null, userId: number, onProjectUpdated: () => void) => {
      if (!canManage || token === null || project === null) {
        return;
      }

      await runMutation(async () => {
        await removeProjectOwner(token, project.id, userId);
        return `User ${userId} removed from ${project.reference_name}.`;
      });
      onProjectUpdated();
    },
  );

  async function runMutation(mutation: () => Promise<string>) {
    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isMutating: true,
      successMessage: null,
    }));

    try {
      const successMessage = await mutation();
      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isMutating: false,
        successMessage,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to complete admin action."),
        isMutating: false,
        successMessage: null,
      }));
    }
  }

  return {
    addOwner,
    canManage,
    changeUserActivation,
    changeUserRole,
    errorMessage: state.errorMessage,
    isLoading: state.isLoading,
    isMutating: state.isMutating,
    refreshUsers,
    removeOwner,
    successMessage: state.successMessage,
    users: state.users,
  };
}
