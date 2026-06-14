import { promises as fs } from "node:fs";
import { dirname, join } from "node:path";
import { expect, test } from "@playwright/test";
import { createCompleteSuiteResult } from "./support/completeSuiteResult";
import { createOperationRecorder } from "./support/operationRecorder";

const apiBase = process.env.VALIDATION_CLIENT_API_BASE || "http://127.0.0.1:8765";

test("complete-worldengine-validation-suite exports structured blocked evidence", async ({ page, request }, testInfo) => {
  const runId = `complete-suite-${Date.now()}`;
  const resultDir = testInfo.outputPath("complete-worldengine-validation-suite");
  const recorder = createOperationRecorder({ resultDir, runId });
  const suite = createCompleteSuiteResult({ resultDir, runId });
  const consoleLines: string[] = [];
  const transcriptLines: string[] = [];

  page.on("console", (message) => {
    if (["warning", "error"].includes(message.type())) {
      consoleLines.push(`${message.type()}: ${message.text()}`);
    }
  });
  page.on("pageerror", (error) => {
    consoleLines.push(`pageerror: ${error.message}`);
  });

  suite.markStepPlanned("P1-01", "phase-1");
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "会话库" })).toBeVisible();
  const pageOpenScreenshot = "screenshots/phase-1-blocked.png";
  await writePageScreenshot(page, join(resultDir, pageOpenScreenshot));
  const pageOpenOperationRef = recorder.recordOperation({
    step_id: "P1-01",
    phase: "phase-1",
    operation_kind: "page_open",
    target: {
      page: "Session Library",
      label: "Validation Client root",
    },
    after: {
      url: page.url(),
      visible_text_summary: "会话库可见",
      screenshot: pageOpenScreenshot,
    },
    artifact_refs: [pageOpenScreenshot],
    result: { status: "executed" },
  });
  suite.markStepExecuted("P1-01", {
    operation_log_ref: pageOpenOperationRef,
    artifact_refs: [pageOpenScreenshot],
  });
  transcriptLines.push("P1-01 opened the Validation Client session library.");

  suite.markStepPlanned("P1-02", "phase-1");
  const startedAt = Date.now();
  const healthResponse = await request.get(`${apiBase}/health/worldengine`);
  const healthPayload = await healthResponse.json();
  const healthApiRef = recorder.recordApiCall({
    phase: "phase-1",
    source_step_id: "P1-02",
    method: "GET",
    url_origin: "validation-client-api",
    path_template: "/health/worldengine",
    path_redacted: "/health/worldengine",
    request_summary: {
      body_shape: [],
      public_input_lengths: {},
      secrets_included: false,
      raw_prompt_included: false,
      direct_harvest: true,
    },
    response_summary: {
      status_code: healthResponse.status(),
      body_shape: Object.keys(healthPayload),
      error_class: classifyWorldEngineBlocker(healthPayload),
    },
    duration_ms: Date.now() - startedAt,
  });
  const blockedReason = classifyWorldEngineBlocker(healthPayload) || "connected_path_not_run_in_blocked_smoke";
  const connectionOperationRef = recorder.recordOperation({
    step_id: "P1-02",
    phase: "phase-1",
    operation_kind: "blocked",
    target: {
      page: "Session Library",
      label: "WorldEngine connection status",
    },
    api_refs: [healthApiRef],
    artifact_refs: ["capability-discovery.json"],
    result: {
      status: "blocked",
      blocked_reason: blockedReason,
    },
  });
  suite.markStepBlocked("P1-02", blockedReason, {
    operation_log_ref: connectionOperationRef,
    api_refs: [healthApiRef],
    artifact_refs: ["capability-discovery.json"],
  });
  transcriptLines.push(`P1-02 classified the run as BLOCKED: ${blockedReason}.`);

  await suite.writeBlockedResult({
    status_reason: `Complete suite stopped at Phase 1: ${blockedReason}`,
    taxonomy: blockedReason,
    worldengine: {
      reachable: Boolean(healthPayload.worldengine?.reachable),
      manifest_seen: Boolean(healthPayload.worldengine?.manifest),
      capabilities: healthPayload.worldengine?.capabilities ?? {},
    },
    operationLog: recorder.getOperationLog(),
    apiLog: recorder.getApiLog(),
    transcriptLines,
    consoleLines,
    screenshotStatuses: [{ name: pageOpenScreenshot, status: "blocked", path: pageOpenScreenshot }],
  });

  const result = JSON.parse(await fs.readFile(join(resultDir, "result.json"), "utf-8"));
  expect(result).toMatchObject({
    schema_version: "0.9.1",
    scenario: "complete-worldengine-validation-suite",
    status: "blocked",
  });
  expect(result.phases).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        phase: "phase-1",
        status: "blocked",
        executed_steps: ["P1-01", "P1-02"],
        blocked_reason: blockedReason,
      }),
    ]),
  );

  const coverage = JSON.parse(await fs.readFile(join(resultDir, "coverage-matrix.json"), "utf-8"));
  expect(coverage.steps["P1-01"].operation_log_ref).toBe(pageOpenOperationRef);
  expect(coverage.steps["P1-02"].api_refs).toEqual([healthApiRef]);
  await expectFile(join(resultDir, "operation-log.jsonl"));
  await expectFile(join(resultDir, "api-log.jsonl"));
  await expectFile(join(resultDir, "api-summary.json"));
  await expectFile(join(resultDir, "console.log"));
  await expectFile(join(resultDir, "transcript.md"));
  await expectFile(join(resultDir, "screenshots/status.json"));
});

function classifyWorldEngineBlocker(healthPayload: any): string | null {
  const worldengine = healthPayload.worldengine || {};
  if (!worldengine.reachable) {
    return "worldengine_unreachable";
  }
  if (!worldengine.openapi) {
    return "missing_worldengine_openapi";
  }
  if (worldengine.capabilities?.world_creation !== "available") {
    return "missing_world_creation_capability";
  }
  return null;
}

async function writePageScreenshot(page: { screenshot: (options: { path: string; fullPage?: boolean }) => Promise<unknown> }, path: string) {
  await fs.mkdir(dirname(path), { recursive: true });
  await page.screenshot({ path, fullPage: true });
}

async function expectFile(path: string) {
  await expect(fs.access(path)).resolves.toBeUndefined();
}
