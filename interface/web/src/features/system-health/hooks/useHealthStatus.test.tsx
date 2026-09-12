import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import type { SystemHealthSnapshot } from "../../../shared/types/system";
import { useHealthStatus } from "./useHealthStatus";

const { getSystemHealth } = vi.hoisted(() => ({
  getSystemHealth: vi.fn<() => Promise<SystemHealthSnapshot>>(),
}));

vi.mock("../../../shared/api/system", () => ({ getSystemHealth }));

const snapshot: SystemHealthSnapshot = {
  name: "OrchFlow",
  stage: "bootstrap",
  status: "ok",
  version: "0.3.33",
};

describe("useHealthStatus", () => {
  it("preserves the latest health snapshot when a refresh fails", async () => {
    getSystemHealth.mockResolvedValueOnce(snapshot).mockRejectedValue(new Error("offline"));
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(() => useHealthStatus(), { wrapper });

    await waitFor(() => expect(result.current.healthStatus).toEqual(snapshot));

    act(() => result.current.refresh());

    await waitFor(() => expect(result.current.errorMessage).toContain("offline"));
    expect(result.current.healthStatus).toEqual(snapshot);
  });
});
