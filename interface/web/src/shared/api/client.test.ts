import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiRequestError, requestJson } from "./client";
import { formatErrorMessage } from "./errors";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("requestJson error handling", () => {
  it("preserves HTTP status, method, path, and string details", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Project not found." }), {
        status: 404,
        statusText: "Not Found",
      }),
    );

    await expect(requestJson("/projects/99", { token: "token" })).rejects.toMatchObject({
      detail: "Project not found.",
      method: "GET",
      path: "/projects/99",
      statusCode: 404,
    });
  });

  it("formats FastAPI validation details for operator-facing messages", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: [
            {
              loc: ["body", "reference_name"],
              msg: "Field required",
              type: "missing",
            },
          ],
        }),
        { status: 422, statusText: "Unprocessable Entity" },
      ),
    );

    let capturedError: unknown;
    try {
      await requestJson("/projects", { body: {}, method: "POST", token: "token" });
    } catch (error) {
      capturedError = error;
    }

    expect(capturedError).toBeInstanceOf(ApiRequestError);
    expect(formatErrorMessage(capturedError, "Unable to register the project.")).toBe(
      "Unable to register the project. Some submitted fields need review. HTTP 422 POST /projects. body.reference_name: Field required",
    );
  });
});
