import { QueryClient } from "@tanstack/react-query";

export const workspaceQueryKeys = {
  health: ["system-health"] as const,
  projects: (token: string) => ["projects", token] as const,
};

export function createWorkspaceQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  });
}
