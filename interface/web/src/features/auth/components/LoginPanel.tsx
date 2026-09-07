import { FormEvent, useState } from "react";

import "./LoginPanel.css";
import { ErrorNotice } from "../../../shared/components/ErrorNotice";

type AuthMode = "login" | "create";

type LoginPanelProps = {
  errorMessage: string | null;
  isLoading: boolean;
  onCreateAccount: (username: string, password: string) => void;
  onSubmit: (username: string, password: string) => void;
};

export function LoginPanel({
  errorMessage,
  isLoading,
  onCreateAccount,
  onSubmit,
}: LoginPanelProps) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (mode === "create") {
      onCreateAccount(username, password);
      return;
    }

    onSubmit(username, password);
  }

  return (
    <section className="login-panel" aria-label="OrchFlow authentication">
      <header className="login-panel__header">
        <span className="login-panel__mark" aria-hidden="true">
          OF
        </span>
        <span className="login-panel__eyebrow">Local operator access</span>
        <h1 className="login-panel__title">OrchFlow</h1>
        <p className="login-panel__copy">
          Sign in to control registered projects, inspect runtime state, and review local
          lifecycle activity from one operator workspace.
        </p>
      </header>

      <div className="login-panel__mode" role="tablist" aria-label="Authentication mode">
        <button
          aria-selected={mode === "login"}
          className="login-panel__mode-button"
          onClick={() => setMode("login")}
          role="tab"
          type="button"
        >
          Login
        </button>
        <button
          aria-selected={mode === "create"}
          className="login-panel__mode-button"
          onClick={() => setMode("create")}
          role="tab"
          type="button"
        >
          Create account
        </button>
      </div>

      <form className="login-panel__form" onSubmit={handleSubmit}>
        <label className="login-panel__field">
          <span>Username</span>
          <input
            autoComplete="username"
            name="username"
            onChange={(event) => setUsername(event.target.value)}
            placeholder="admin-user"
            value={username}
          />
        </label>

        <label className="login-panel__field">
          <span>Password</span>
          <input
            autoComplete={mode === "create" ? "new-password" : "current-password"}
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            placeholder="password123"
            type="password"
            value={password}
          />
        </label>

        <div className="login-panel__actions">
          <button className="login-panel__button" disabled={isLoading} type="submit">
            {isLoading ? "Working..." : mode === "create" ? "Create account" : "Login"}
          </button>
          {errorMessage !== null ? (
            <ErrorNotice
              className="login-panel__error"
              message={errorMessage}
              title={mode === "create" ? "Account creation failed" : "Login failed"}
            />
          ) : null}
        </div>
      </form>

      <p className="login-panel__hint">
        Account creation is role-neutral. The first local user becomes the bootstrap admin;
        later public sign-ups enter as members unless an admin changes their role.
      </p>
    </section>
  );
}
