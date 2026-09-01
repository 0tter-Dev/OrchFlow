import { startTransition, useEffect, useEffectEvent, useState } from "react";

import { formatErrorMessage } from "../../../shared/api/errors";
import { getCurrentUser, loginUser } from "../../../shared/api/auth";
import type { UserSummary } from "../../../shared/types/auth";

const AUTH_TOKEN_STORAGE_KEY = "orchflow.auth.token";

type AuthState = {
  currentUser: UserSummary | null;
  errorMessage: string | null;
  isLoading: boolean;
  token: string | null;
};

const initialState: AuthState = {
  currentUser: null,
  errorMessage: null,
  isLoading: true,
  token: null,
};

export function useAuthSession() {
  const [state, setState] = useState<AuthState>(initialState);

  const hydrateFromToken = useEffectEvent(async (token: string) => {
    setState({
      currentUser: null,
      errorMessage: null,
      isLoading: true,
      token,
    });

    try {
      const currentUser = await getCurrentUser(token);
      startTransition(() => {
        setState({
          currentUser,
          errorMessage: null,
          isLoading: false,
          token,
        });
      });
    } catch (error) {
      window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      const message = formatErrorMessage(error, "Unable to validate the session.");
      setState({
        currentUser: null,
        errorMessage: message,
        isLoading: false,
        token: null,
      });
    }
  });

  useEffect(() => {
    const storedToken = window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
    if (storedToken === null || storedToken.length === 0) {
      setState({
        currentUser: null,
        errorMessage: null,
        isLoading: false,
        token: null,
      });
      return;
    }

    void hydrateFromToken(storedToken);
  }, [hydrateFromToken]);

  const login = useEffectEvent(async (username: string, password: string) => {
    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoading: true,
    }));

    try {
      const payload = await loginUser({ password, username });
      window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, payload.access_token);
      await hydrateFromToken(payload.access_token);
    } catch (error) {
      const message = formatErrorMessage(error, "Unable to sign in.");
      setState({
        currentUser: null,
        errorMessage: message,
        isLoading: false,
        token: null,
      });
    }
  });

  function logout() {
    window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
    setState({
      currentUser: null,
      errorMessage: null,
      isLoading: false,
      token: null,
    });
  }

  return {
    currentUser: state.currentUser,
    errorMessage: state.errorMessage,
    isLoading: state.isLoading,
    login,
    logout,
    token: state.token,
  };
}
