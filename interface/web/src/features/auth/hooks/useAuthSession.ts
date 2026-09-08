import { startTransition, useCallback, useEffect, useState } from "react";

import { formatErrorMessage } from "../../../shared/api/errors";
import { getCurrentUser, loginUser, registerUser } from "../../../shared/api/auth";
import type { UserSummary } from "../../../shared/types/auth";

const AUTH_TOKEN_STORAGE_KEY = "orchflow.auth.token";

type AuthState = {
  currentUser: UserSummary | null;
  errorMessage: string | null;
  isLoading: boolean;
  statusMessage: string | null;
  token: string | null;
};

const initialState: AuthState = {
  currentUser: null,
  errorMessage: null,
  isLoading: true,
  statusMessage: null,
  token: null,
};

export function useAuthSession() {
  const [state, setState] = useState<AuthState>(initialState);

  const hydrateFromToken = useCallback(async (token: string) => {
    setState({
      currentUser: null,
      errorMessage: null,
      isLoading: true,
      statusMessage: "Validating session...",
      token,
    });

    try {
      const currentUser = await getCurrentUser(token);
      startTransition(() => {
        setState({
          currentUser,
          errorMessage: null,
          isLoading: false,
          statusMessage: null,
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
        statusMessage: null,
        token: null,
      });
    }
  }, []);

  useEffect(() => {
    const storedToken = window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
    if (storedToken === null || storedToken.length === 0) {
      setState({
        currentUser: null,
        errorMessage: null,
        isLoading: false,
        statusMessage: null,
        token: null,
      });
      return;
    }

    void hydrateFromToken(storedToken);
  }, [hydrateFromToken]);

  const login = useCallback(async (username: string, password: string) => {
    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoading: true,
      statusMessage: "Signing in...",
    }));

    try {
      const payload = await loginUser({ password, username });
      window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, payload.access_token);
      await hydrateFromToken(payload.access_token);
    } catch (error) {
      const message = formatErrorMessage(error, "Unable to sign in.");
      window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      setState({
        currentUser: null,
        errorMessage: message,
        isLoading: false,
        statusMessage: null,
        token: null,
      });
    }
  }, [hydrateFromToken]);

  const createAccount = useCallback(async (username: string, password: string) => {
    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoading: true,
      statusMessage: "Creating account...",
    }));

    try {
      await registerUser({ password, username });
      setState((currentState) => ({
        ...currentState,
        statusMessage: "Account created. Signing in...",
      }));
      const payload = await loginUser({ password, username });
      window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, payload.access_token);
      await hydrateFromToken(payload.access_token);
    } catch (error) {
      const message = formatErrorMessage(error, "Unable to create the account.");
      window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      setState({
        currentUser: null,
        errorMessage: message,
        isLoading: false,
        statusMessage: null,
        token: null,
      });
    }
  }, [hydrateFromToken]);

  function logout() {
    window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
    setState({
      currentUser: null,
      errorMessage: null,
      isLoading: false,
      statusMessage: null,
      token: null,
    });
  }

  return {
    createAccount,
    currentUser: state.currentUser,
    errorMessage: state.errorMessage,
    isLoading: state.isLoading,
    login,
    logout,
    statusMessage: state.statusMessage,
    token: state.token,
  };
}
