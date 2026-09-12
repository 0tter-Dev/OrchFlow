import { useQuery } from "@tanstack/react-query";

import { formatErrorMessage } from "../../../shared/api/errors";
import { getSystemHealth } from "../../../shared/api/system";
import { workspaceQueryKeys } from "../../../app/query-client";

export function useHealthStatus() {
  const query = useQuery({
    queryKey: workspaceQueryKeys.health,
    queryFn: getSystemHealth,
  });

  return {
    errorMessage:
      query.error === null
        ? null
        : formatErrorMessage(query.error, "Unable to reach the OrchFlow API."),
    healthStatus: query.data ?? null,
    isLoading: query.isLoading,
    lastUpdated: query.dataUpdatedAt === 0 ? null : new Date(query.dataUpdatedAt),
    refresh: () => {
      void query.refetch();
    },
  };
}
