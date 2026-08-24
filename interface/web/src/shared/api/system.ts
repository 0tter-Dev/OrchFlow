import { requestJson } from "./client";
import type { SystemHealthSnapshot } from "../types/system";

export function getSystemHealth(): Promise<SystemHealthSnapshot> {
  return requestJson<SystemHealthSnapshot>("/health");
}
