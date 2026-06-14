import { access, mkdtemp, readFile, rm } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createCompleteSuiteResult } from "../../e2e/support/completeSuiteResult";

let resultDir: string;

async function readJson(path: string) {
  return JSON.parse(await readFile(path, "utf-8"));
}

async function expectFile(path: string) {
  await expect(access(path)).resolves.toBeUndefined();
}

describe("completeSuiteResult", () => {
  beforeEach(async () => {
    resultDir = await mkdtemp(join(tmpdir(), "complete-suite-result-"));
  });

  afterEach(async () => {
    await rm(resultDir, { recursive: true, force: true });
  });

  it("exports a structured BLOCKED handoff when WorldEngine is unreachable", async () => {
    const suite = createCompleteSuiteResult({
      resultDir,
      runId: "run-1",
      now: () => "2026-06-14T00:00:00.000Z",
    });

    suite.markStepPlanned("P1-01", "phase-1");
    suite.markStepExecuted("P1-01", {
      operation_log_ref: "operation-log:0001",
      artifact_refs: ["screenshots/phase-1-blocked.png"],
    });
    suite.markStepPlanned("P1-02", "phase-1");
    suite.markStepBlocked("P1-02", "worldengine_unreachable", {
      operation_log_ref: "operation-log:0002",
      api_refs: ["api-log:0001"],
      artifact_refs: ["capability-discovery.json"],
    });

    await suite.writeBlockedResult({
      status_reason: "WorldEngine public API is unreachable",
      taxonomy: "worldengine_unreachable",
      worldengine: {
        reachable: false,
        manifest_seen: false,
        capabilities: {},
      },
      operationLog: [
        { step_id: "P1-01", result: { status: "executed" } },
        { step_id: "P1-02", result: { status: "blocked", blocked_reason: "worldengine_unreachable" } },
      ],
      apiLog: [
        {
          api_ref: "api-log:0001",
          phase: "phase-1",
          source_step_id: "P1-02",
          response_summary: { status_code: 503, error_class: "worldengine_unreachable" },
        },
      ],
      transcriptLines: ["WorldEngine health check returned unreachable."],
      consoleLines: ["network GET /health/worldengine failed with public 503"],
      screenshotStatuses: [{ name: "phase-1-blocked.png", status: "blocked" }],
    });

    for (const artifact of [
      "result.json",
      "coverage-matrix.json",
      "command-matrix.md",
      "operation-log.jsonl",
      "api-log.jsonl",
      "api-summary.json",
      "capability-discovery.json",
      "redaction-report.json",
      "console.log",
      "transcript.md",
      "screenshots/status.json",
    ]) {
      await expectFile(join(resultDir, artifact));
    }

    const result = await readJson(join(resultDir, "result.json"));
    expect(result).toMatchObject({
      schema_version: "0.9.1",
      scenario: "complete-worldengine-validation-suite",
      status: "blocked",
      status_reason: "WorldEngine public API is unreachable",
      worldengine: {
        reachable: false,
        manifest_seen: false,
      },
      phases: [
        {
          phase: "phase-1",
          status: "blocked",
          executed_steps: ["P1-01", "P1-02"],
          blocked_reason: "worldengine_unreachable",
          pass_source: "none",
        },
      ],
      redaction: {
        status: "pass",
        blocking_findings: [],
      },
    });

    const transcript = await readFile(join(resultDir, "transcript.md"), "utf-8");
    expect(transcript).toContain("WorldEngine health check returned unreachable.");
  });

  it("records phase-level BLOCKED when a required capability is missing", async () => {
    const suite = createCompleteSuiteResult({ resultDir, runId: "run-1" });

    suite.markStepPlanned("P1-01", "phase-1");
    suite.markStepExecuted("P1-01", { operation_log_ref: "operation-log:0001" });
    suite.markStepPlanned("P3-07", "phase-3");
    suite.markStepBlocked("P3-07", "missing_worldengine_capability", {
      operation_log_ref: "operation-log:0002",
      api_refs: ["api-log:0004"],
    });
    await suite.writeCoverageMatrix();
    await suite.writeResultJson("blocked", {
      status_reason: "Agent memory continuity capability is missing",
      worldengine: { reachable: true, manifest_seen: true, capabilities: { world_creation: "available" } },
    });

    const result = await readJson(join(resultDir, "result.json"));
    expect(result.phases).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          phase: "phase-3",
          status: "blocked",
          executed_steps: ["P3-07"],
          blocked_reason: "missing_worldengine_capability",
        }),
      ]),
    );
  });

  it("does not allow PASS when required artifacts are missing", async () => {
    const suite = createCompleteSuiteResult({ resultDir, runId: "run-1" });

    await suite.writeResultJson("pass", {
      status_reason: "requested pass without required artifacts",
      worldengine: { reachable: true, manifest_seen: true, capabilities: {} },
    });

    const result = await readJson(join(resultDir, "result.json"));
    expect(result.status).toBe("partial");
    expect(result.status_reason).toContain("missing required artifacts");
  });

  it("forces FAIL when redaction has blocking findings", async () => {
    const suite = createCompleteSuiteResult({
      resultDir,
      runId: "run-1",
      redactionFindings: [{ path: "api-log.jsonl", marker: "authorization" }],
    });

    await suite.writeResultJson("blocked", {
      status_reason: "blocked before redaction scan",
      worldengine: { reachable: false, manifest_seen: false, capabilities: {} },
    });

    const result = await readJson(join(resultDir, "result.json"));
    expect(result.status).toBe("fail");
    expect(result.redaction).toEqual({
      status: "fail",
      blocking_findings: [{ path: "api-log.jsonl", marker: "authorization" }],
    });
  });

  it("writes coverage matrix entries for planned, executed, and blocked steps", async () => {
    const suite = createCompleteSuiteResult({ resultDir, runId: "run-1" });

    suite.markStepPlanned("P1-01", "phase-1");
    suite.markStepExecuted("P1-01", {
      operation_log_ref: "operation-log:0001",
      api_refs: [],
      artifact_refs: ["screenshots/phase-1-open.png"],
    });
    suite.markStepPlanned("P1-02", "phase-1");
    suite.markStepBlocked("P1-02", "worldengine_unreachable", {
      operation_log_ref: "operation-log:0002",
      api_refs: ["api-log:0001"],
    });
    await suite.writeCoverageMatrix();

    const coverage = await readJson(join(resultDir, "coverage-matrix.json"));
    expect(coverage.steps).toMatchObject({
      "P1-01": {
        phase: "phase-1",
        planned: true,
        executed: true,
        not_run: false,
        blocked: false,
        operation_log_ref: "operation-log:0001",
        api_refs: [],
        artifact_refs: ["screenshots/phase-1-open.png"],
      },
      "P1-02": {
        phase: "phase-1",
        planned: true,
        executed: true,
        not_run: false,
        blocked: true,
        blocked_reason: "worldengine_unreachable",
        operation_log_ref: "operation-log:0002",
        api_refs: ["api-log:0001"],
      },
    });
  });
});
