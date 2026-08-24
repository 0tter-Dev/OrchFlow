const DEFAULT_API_BASE_URL = "http://localhost:8000";

export function getApiBaseUrl(): string {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  if (configuredBaseUrl === undefined || configuredBaseUrl.length === 0) {
    return DEFAULT_API_BASE_URL;
  }

  return configuredBaseUrl.replace(/\/$/, "");
}
