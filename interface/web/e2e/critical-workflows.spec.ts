import { expect, test, type Page } from "@playwright/test";

type Project = {
  action_mappings: Array<{ canonical_action: string; configured_by_user_id: number; script_label: string; source: string }>;
  created_by_user_id: number;
  description: string | null;
  id: number;
  lifecycle_configuration_health: "complete" | "partial" | "blocked";
  lifecycle_function_configurations: Array<{ canonical_action: string; description: string; preferred_script_identifier: string; script_label: string | null; state: string }>;
  lifecycle_script_path: string;
  owner_user_ids: number[];
  project_root_path: string;
  reference_name: string;
};

const member = { id: 1, is_active: true, role: "member", username: "browser-user" };
const preferences = { locale: "en-US", project_view_mode: "list", status_refresh_interval_seconds: 300, user_id: 1 };
const runtimeSnapshot = { application_reachable: null, application_url: null, inspected_at: "2026-09-13T00:00:00Z", known_port: null, process_snapshots: [], project_id: 1, status: "stopped", status_reason: "The project is not running.", uptime_seconds: null };

function completeProject(): Project {
  const lifecycle_function_configurations = ["status", "start", "stop", "restart"].map((canonical_action) => ({
    canonical_action,
    description: `${canonical_action} lifecycle action`,
    preferred_script_identifier: canonical_action.toUpperCase(),
    script_label: canonical_action.toUpperCase(),
    state: "configured",
  }));
  return {
    action_mappings: lifecycle_function_configurations.map((configuration) => ({ ...configuration, configured_by_user_id: 1, source: "user_defined" })),
    created_by_user_id: 1,
    description: "A deterministic browser test project.",
    id: 1,
    lifecycle_configuration_health: "complete",
    lifecycle_function_configurations,
    lifecycle_script_path: "C:\\fixture\\control.bat",
    owner_user_ids: [1],
    project_root_path: "C:\\fixture",
    reference_name: "browser-fixture",
  };
}

async function installApiMock(page: Page, initialProjects: Project[] = []) {
  const requests: Array<{ body: unknown; method: string; path: string }> = [];
  let projects = initialProjects;

  await page.route("**/orchflow-api/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname.replace("/orchflow-api", "");
    const body = request.postData() === null ? null : request.postDataJSON();
    requests.push({ body, method: request.method(), path });
    const respond = (payload: unknown) => route.fulfill({ body: JSON.stringify(payload), contentType: "application/json", status: 200 });

    if (path === "/health") return respond({ name: "OrchFlow", stage: "implementation", status: "ok", version: "0.3.36" });
    if (path === "/auth/register" && request.method() === "POST") return respond(member);
    if (path === "/auth/login" && request.method() === "POST") return respond({ access_token: "browser-token", expires_in_seconds: 3600, token_type: "bearer" });
    if (path === "/auth/me") return respond(member);
    if (path === "/auth/me/preferences") return respond(preferences);
    if (path === "/projects" && request.method() === "GET") return respond(projects);
    if (path === "/projects" && request.method() === "POST") {
      const registration = body as { description: string | null; lifecycle_script_path: string; project_root_path: string; reference_name: string };
      projects = [{ ...completeProject(), ...registration }];
      return respond(projects[0]);
    }
    if (path === "/projects/runtime-inspections") return respond(projects.map((project) => ({ ...runtimeSnapshot, project_id: project.id })));
    if (path === "/projects/1") return respond(projects[0]);
    if (path === "/projects/1/runtime") return respond(runtimeSnapshot);
    if (path === "/local-path-selection") {
      const kind = (body as { kind: string }).kind;
      return respond({ path: kind === "project_root" ? "C:\\fixture" : "C:\\fixture\\control.bat", status: "selected" });
    }
    if (path === "/projects/1/lifecycle/start") return respond({ canonical_action: "start", command_identifier: "START", exit_code: 0, project_id: 1, runtime_status: "running", stderr: "", stdout: "started", succeeded: true });
    if (path === "/ai/status") return respond({ enabled: false, message: "AI assistance is disabled.", ready_for_requests: false });
    if (path === "/ai/models") return respond({ default_model: null, models: [] });
    return respond([]);
  });
  return requests;
}

test("creates an account and opens the authenticated workspace", async ({ page }) => {
  const requests = await installApiMock(page);
  await page.goto("/");
  await page.getByRole("tab", { name: "Create account" }).click();
  await page.getByLabel("Username").fill("browser-user");
  await page.locator('input[name="password"]').fill("password123");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.locator(".topbar__user")).toContainText("browser-user");
  expect(requests.map((request) => request.path)).toEqual(expect.arrayContaining(["/auth/register", "/auth/login", "/auth/me"]));
});

test("registers a project using authenticated path selection", async ({ page }) => {
  await page.addInitScript(() => window.localStorage.setItem("orchflow.auth.token", "browser-token"));
  const requests = await installApiMock(page);
  await page.goto("/projects");
  await page.getByRole("button", { name: "Register project" }).click();
  await page.getByLabel("Name").fill("browser-fixture");
  await page.getByRole("button", { name: "Browse" }).nth(0).click();
  await page.getByRole("button", { name: "Browse" }).nth(1).click();
  await page.getByRole("button", { name: "Register", exact: true }).click();

  await expect(page.getByText("browser-fixture registered successfully.")).toBeVisible();
  expect(requests.filter((request) => request.path === "/local-path-selection")).toHaveLength(2);
  expect(requests.find((request) => request.path === "/projects" && request.method === "POST")?.body).toMatchObject({ lifecycle_script_path: "C:\\fixture\\control.bat", project_root_path: "C:\\fixture", reference_name: "browser-fixture" });
});

test("presents confirmation before a mutable lifecycle action", async ({ page }) => {
  await page.addInitScript(() => window.localStorage.setItem("orchflow.auth.token", "browser-token"));
  const requests = await installApiMock(page, [completeProject()]);
  await page.goto("/projects");
  await page.getByRole("button", { name: "start configured", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "Confirm lifecycle action" })).toBeVisible();
  expect(requests.some((request) => request.path === "/projects/1/lifecycle/start")).toBe(false);
});
