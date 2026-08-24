import { getApiBaseUrl } from "../config/env";

export class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly statusCode?: number,
    readonly detail?: string,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

type RequestJsonOptions = {
  body?: unknown;
  method?: "GET" | "POST";
  signal?: AbortSignal;
  token?: string | null;
};

type ErrorPayload = {
  detail?: string;
};

function buildHeaders(options: RequestJsonOptions): Headers {
  const headers = new Headers({
    Accept: "application/json",
  });

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  if (options.token !== undefined && options.token !== null && options.token.length > 0) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  return headers;
}

async function buildApiError(response: Response): Promise<ApiRequestError> {
  let detail: string | undefined;

  try {
    const payload = (await response.json()) as ErrorPayload;
    detail = payload.detail;
  } catch {
    const text = await response.text();
    detail = text.length > 0 ? text : undefined;
  }

  const message = detail ?? `Request failed with status ${response.status}.`;
  return new ApiRequestError(message, response.status, detail);
}

export async function requestJson<T>(
  path: string,
  options: RequestJsonOptions = {},
): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    headers: buildHeaders(options),
    method: options.method ?? "GET",
    signal: options.signal,
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
