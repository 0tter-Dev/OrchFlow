import { getApiBaseUrl } from "../config/env";

export class ApiRequestError extends Error {
  constructor(message: string, readonly statusCode?: number) {
    super(message);
    this.name = "ApiRequestError";
  }
}

export async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new ApiRequestError(`Request failed with status ${response.status}.`, response.status);
  }

  return (await response.json()) as T;
}
