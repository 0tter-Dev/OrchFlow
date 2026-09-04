import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      "/orchflow-api": {
        rewrite: (path) => path.replace(/^\/orchflow-api/, ""),
        target: "http://localhost:8000",
      },
    },
  },
  test: {
    css: true,
    environment: "jsdom",
    setupFiles: "./vitest.setup.ts",
  },
});
