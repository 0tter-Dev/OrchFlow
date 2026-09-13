import { defineConfig, devices } from "@playwright/test";
import { fileURLToPath } from "node:url";

const configDirectory = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "pnpm build && pnpm exec vite preview --host 127.0.0.1 --port 4173",
    cwd: configDirectory,
    reuseExistingServer: !process.env.CI,
    url: "http://127.0.0.1:4173",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
