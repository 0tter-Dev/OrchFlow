import { ApiRequestError } from "./client";

function statusDescription(statusCode: number): string {
  if (statusCode === 400) {
    return "The request was rejected by OrchFlow.";
  }
  if (statusCode === 401) {
    return "The session is missing or expired.";
  }
  if (statusCode === 403) {
    return "The current user is not allowed to perform this action.";
  }
  if (statusCode === 404) {
    return "The requested OrchFlow resource was not found.";
  }
  if (statusCode === 409) {
    return "The action conflicts with the current project state.";
  }
  if (statusCode === 422) {
    return "Some submitted fields need review.";
  }
  if (statusCode >= 500) {
    return "The OrchFlow API returned a server error.";
  }
  return "The OrchFlow API returned an error.";
}

export function formatErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiRequestError) {
    const location =
      error.method !== undefined && error.path !== undefined
        ? ` ${error.method} ${error.path}`
        : "";
    const detail =
      error.validationMessages.length > 0
        ? error.validationMessages.join("; ")
        : error.detail ?? error.message;
    return `${fallback} ${statusDescription(error.statusCode ?? 0)}${
      error.statusCode === undefined ? "" : ` HTTP ${error.statusCode}${location}.`
    } ${detail}`;
  }

  return error instanceof Error ? `${fallback} ${error.message}` : fallback;
}
