import { getApiBaseUrl } from "../config/env";

export class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly statusCode?: number,
    readonly detail?: string,
    readonly method?: string,
    readonly path?: string,
    readonly validationMessages: string[] = [],
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

type RequestJsonOptions = {
  body?: unknown;
  method?: "DELETE" | "GET" | "PATCH" | "POST";
  signal?: AbortSignal;
  token?: string | null;
};

type ErrorPayload = {
  detail?: string | ValidationErrorPayload[];
};

type ValidationErrorPayload = {
  loc?: Array<number | string>;
  msg?: string;
  type?: string;
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

function formatValidationError(error: ValidationErrorPayload): string {
  const location = error.loc?.join(".") ?? "request";
  const message = error.msg ?? error.type ?? "Invalid value.";
  return `${location}: ${message}`;
}

async function buildApiError(
  response: Response,
  options: Required<Pick<RequestJsonOptions, "method">> & Pick<RequestJsonOptions, "body">,
  path: string,
): Promise<ApiRequestError> {
  let detail: string | undefined;
  let validationMessages: string[] = [];
  const text = await response.text();

  if (text.length > 0) {
    try {
      const payload = JSON.parse(text) as ErrorPayload;
      if (Array.isArray(payload.detail)) {
        validationMessages = payload.detail.map(formatValidationError);
        detail = validationMessages.join("; ");
      } else {
        detail = payload.detail;
      }
    } catch {
      detail = text;
    }
  }

  const statusLabel = response.statusText || "Request failed";
  const message = detail ?? `${statusLabel} (${response.status}).`;
  return new ApiRequestError(
    message,
    response.status,
    detail,
    options.method,
    path,
    validationMessages,
  );
}

export async function requestJson<T>(
  path: string,
  options: RequestJsonOptions = {},
): Promise<T> {
  const method = options.method ?? "GET";
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    headers: buildHeaders(options),
    method,
    signal: options.signal,
  });

  if (!response.ok) {
    throw await buildApiError(response, { body: options.body, method }, path);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
