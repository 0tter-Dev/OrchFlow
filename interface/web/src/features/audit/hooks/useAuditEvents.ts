import { useEffect, useEffectEvent, useState } from "react";

import { listAuditEvents } from "../../../shared/api/audit";
import type { UserSummary } from "../../../shared/types/auth";
import type { AuditEventSummary } from "../../../shared/types/audit";

type AuditEventsState = {
  errorMessage: string | null;
  events: AuditEventSummary[];
  isLoading: boolean;
};

const initialState: AuditEventsState = {
  errorMessage: null,
  events: [],
  isLoading: false,
};

function buildErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback;
}

export function useAuditEvents(token: string | null, currentUser: UserSummary | null) {
  const [state, setState] = useState<AuditEventsState>(initialState);
  const canLoadAuditEvents = token !== null && currentUser?.role === "admin";

  const refresh = useEffectEvent(async () => {
    if (!canLoadAuditEvents || token === null) {
      return;
    }

    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoading: true,
    }));

    try {
      const events = await listAuditEvents(token);
      setState({
        errorMessage: null,
        events,
        isLoading: false,
      });
    } catch (error) {
      setState((currentState) => ({
        ...currentState,
        errorMessage: buildErrorMessage(error, "Unable to load audit events."),
        isLoading: false,
      }));
    }
  });

  useEffect(() => {
    if (!canLoadAuditEvents) {
      setState(initialState);
      return;
    }

    void refresh();
  }, [canLoadAuditEvents, refresh]);

  return {
    canLoadAuditEvents,
    errorMessage: state.errorMessage,
    events: state.events,
    isLoading: state.isLoading,
    refresh,
  };
}
