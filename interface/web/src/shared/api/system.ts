import { requestJson } from "./client";
import type { SystemHealthSnapshot } from "../types/system";

export type ConfigurationHealth = {
  status: "ready" | "warning";
  groups: Array<{ concern: string; status: string; remediation: string }>;
};

export function getSystemHealth(): Promise<SystemHealthSnapshot> {
  return requestJson<SystemHealthSnapshot>("/health");
}

export function getConfigurationHealth(): Promise<ConfigurationHealth> {
  return requestJson<ConfigurationHealth>("/system/config/health");
}
