import { defineConfig } from "@playwright/test";

const webPort = Number(process.env.VALIDATION_CLIENT_WEB_PORT || 5173);
const apiBase = process.env.VALIDATION_CLIENT_API_BASE || "http://127.0.0.1:8765";
const outputDir =
  process.env.VALIDATION_CLIENT_E2E_OUTPUT_DIR ||
  "../../docs/milestones/v0.9.1-complete-suite-runner-and-operation-recording/validation-runs/playwright-artifacts";

export default defineConfig({
  testDir: "./e2e",
  outputDir,
  timeout: 90_000,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL: `http://127.0.0.1:${webPort}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command:
        "WORLDENGINE_VALIDATION_DATABASE_PATH=.worldengine-validation-client/e2e.sqlite3 pnpm --dir ../.. run dev:api:e2e",
      url: `${apiBase}/health`,
      reuseExistingServer: true,
      timeout: 30_000,
    },
    {
      command: `VITE_API_BASE_URL=${apiBase} pnpm dev --host 127.0.0.1 --port ${webPort} --strictPort`,
      url: `http://127.0.0.1:${webPort}`,
      reuseExistingServer: true,
      timeout: 30_000,
    },
  ],
});
