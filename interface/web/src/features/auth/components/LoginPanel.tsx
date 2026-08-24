import { FormEvent, useState } from "react";

import "./LoginPanel.css";

type LoginPanelProps = {
  errorMessage: string | null;
  isLoading: boolean;
  onSubmit: (username: string, password: string) => void;
};

export function LoginPanel({ errorMessage, isLoading, onSubmit }: LoginPanelProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(username, password);
  }

  return (
    <section className="login-panel">
      <header>
        <span className="login-panel__eyebrow">Operator access</span>
        <h2 className="login-panel__title">Sign in to OrchFlow</h2>
        <p className="login-panel__copy">
          Use the same OrchFlow account already supported by the mirrored API and CLI
          surfaces. The first registered user is still the bootstrap admin.
        </p>
      </header>

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
            autoComplete="current-password"
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            placeholder="password123"
            type="password"
            value={password}
          />
        </label>

        <div className="login-panel__actions">
          <button className="login-panel__button" disabled={isLoading} type="submit">
            {isLoading ? "Signing in..." : "Open operator session"}
          </button>
          {errorMessage !== null ? <div className="login-panel__error">{errorMessage}</div> : null}
        </div>
      </form>

      <p className="login-panel__hint">
        If no project appears after login, register it through the existing API or CLI surface
        first. This PR focuses on the first useful operator flow for already managed projects.
      </p>
    </section>
  );
}
