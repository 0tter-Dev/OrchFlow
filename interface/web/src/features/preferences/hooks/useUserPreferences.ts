import { startTransition, useEffect, useEffectEvent, useState } from "react";

import { formatErrorMessage } from "../../../shared/api/errors";
import {
  getUserPreferences,
  updateUserPreferences,
} from "../../../shared/api/preferences";
import type {
  UserPreferences,
  UserPreferencesUpdate,
} from "../../../shared/types/preferences";

type UserPreferencesState = {
  errorMessage: string | null;
  isLoading: boolean;
  isSaving: boolean;
  message: string | null;
  preferences: UserPreferences | null;
};

const initialState: UserPreferencesState = {
  errorMessage: null,
  isLoading: false,
  isSaving: false,
  message: null,
  preferences: null,
};

export function useUserPreferences(token: string | null) {
  const [state, setState] = useState<UserPreferencesState>(initialState);

  const refresh = useEffectEvent(async () => {
    if (token === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoading: true,
      message: null,
    }));

    try {
      const preferences = await getUserPreferences(token);
      startTransition(() => {
        setState((currentState) => ({
          ...currentState,
          errorMessage: null,
          isLoading: false,
          preferences,
        }));
      });
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to load user preferences."),
        isLoading: false,
      }));
    }
  });

  useEffect(() => {
    if (token === null) {
      setState(initialState);
      return;
    }

    void refresh();
  }, [refresh, token]);

  const update = useEffectEvent(async (payload: UserPreferencesUpdate) => {
    if (token === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isSaving: true,
      message: null,
    }));

    try {
      const preferences = await updateUserPreferences(token, payload);
      setState((currentState) => ({
        ...currentState,
        errorMessage: null,
        isSaving: false,
        message: "Preferences saved.",
        preferences,
      }));
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: formatErrorMessage(error, "Unable to save user preferences."),
        isSaving: false,
      }));
    }
  });

  return {
    errorMessage: state.errorMessage,
    isLoading: state.isLoading,
    isSaving: state.isSaving,
    message: state.message,
    preferences: state.preferences,
    refresh,
    update,
  };
}
