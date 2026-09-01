import { useEffect, useEffectEvent, useState } from "react";

import { formatErrorMessage } from "../../../shared/api/errors";
import { getSystemHealth } from "../../../shared/api/system";
import type { SystemHealthSnapshot } from "../../../shared/types/system";

type HealthStatusState = {
  errorMessage: string | null;
  healthStatus: SystemHealthSnapshot | null;
  isLoading: boolean;
  lastUpdated: Date | null;
};

const initialState: HealthStatusState = {
  errorMessage: null,
  healthStatus: null,
  isLoading: true,
  lastUpdated: null,
};

export function useHealthStatus() {
  const [state, setState] = useState<HealthStatusState>(initialState);

  const refresh = useEffectEvent(async () => {
    setState((currentState) => ({
      ...currentState,
      errorMessage: null,
      isLoading: true,
    }));

    try {
      const healthStatus = await getSystemHealth();
      setState({
        errorMessage: null,
        healthStatus,
        isLoading: false,
        lastUpdated: new Date(),
      });
    } catch (error) {
      const message = formatErrorMessage(error, "Unable to reach the OrchFlow API.");
      setState({
        errorMessage: message,
        healthStatus: null,
        isLoading: false,
        lastUpdated: new Date(),
      });
    }
  });

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    errorMessage: state.errorMessage,
    healthStatus: state.healthStatus,
    isLoading: state.isLoading,
    lastUpdated: state.lastUpdated,
    refresh,
  };
}
