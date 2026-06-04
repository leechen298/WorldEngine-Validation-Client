import { defineConfig } from "@playwright/test";

const webPort = Number(process.env.VALIDATION_CLIENT_WEB_PORT || 5173);

export default defineConfig({
  testDir: "./e2e",
  outputDir: "../../docs/milestones/v0.7-agent-autonomous-validation/validation-runs/playwright-artifacts",
  timeout: 90_000,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL: `http://127.0.0.1:${webPort}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
});
