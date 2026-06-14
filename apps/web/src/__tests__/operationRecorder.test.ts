import { mkdtemp, readFile, rm } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  createOperationRecorder,
  redactText,
  scanForBlockingMarkers,
} from "../../e2e/support/operationRecorder";

let resultDir: string;

async function readJsonl(path: string) {
  const content = await readFile(path, "utf-8");
  return content
    .trim()
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

describe("operationRecorder", () => {
  beforeEach(async () => {
    resultDir = await mkdtemp(join(tmpdir(), "operation-recorder-"));
  });

  afterEach(async () => {
    await rm(resultDir, { recursive: true, force: true });
  });

  it("records UI operations as contract-shaped JSONL entries", async () => {
    const recorder = createOperationRecorder({
      resultDir,
      runId: "run-1",
      actor: "codex-agent",
      now: () => "2026-06-14T00:00:00.000Z",
    });

    const operationRef = recorder.recordOperation({
      step_id: "P1-05",
      phase: "phase-1",
      operation_kind: "click",
      target: {
        page: "Session Library",
        role: "button",
        label: "创建世界",
      },
      before: {
        url: "http://127.0.0.1:5173/",
        visible_text_summary: "会话库可见",
        screenshot: "screenshots/phase-1-before-create-world.png",
      },
      after: {
        url: "http://127.0.0.1:5173/",
        visible_text_summary: "运行控制可见",
        screenshot: "screenshots/phase-1-after-create-world.png",
      },
      api_refs: ["api-log:0001"],
      artifact_refs: ["world-creation-summary.json"],
      result: { status: "executed" },
    });
    await recorder.writeAll();

    expect(operationRef).toBe("operation-log:0001");
    const [entry] = await readJsonl(join(resultDir, "operation-log.jsonl"));
    expect(entry).toMatchObject({
      schema_version: "0.9.0",
      run_id: "run-1",
      operation_ref: "operation-log:0001",
      step_id: "P1-05",
      phase: "phase-1",
      actor: "codex-agent",
      operation_kind: "click",
      target: {
        page: "Session Library",
        role: "button",
        label: "创建世界",
        test_id: null,
        selector: null,
      },
      before: {
        url: "http://127.0.0.1:5173/",
        visible_text_summary: "会话库可见",
        screenshot: "screenshots/phase-1-before-create-world.png",
      },
      after: {
        url: "http://127.0.0.1:5173/",
        visible_text_summary: "运行控制可见",
        screenshot: "screenshots/phase-1-after-create-world.png",
      },
      api_refs: ["api-log:0001"],
      artifact_refs: ["world-creation-summary.json"],
      result: {
        status: "executed",
        blocked_reason: null,
        error_message: null,
      },
      timestamp: "2026-06-14T00:00:00.000Z",
    });
  });

  it("records blocked operations in operation-log.jsonl", async () => {
    const recorder = createOperationRecorder({ resultDir, runId: "run-1" });

    recorder.recordOperation({
      step_id: "P3-07",
      phase: "phase-3",
      operation_kind: "blocked",
      target: { page: "Runtime Console", label: "Consolidate" },
      result: {
        status: "blocked",
        blocked_reason: "missing_client_control",
      },
    });
    await recorder.writeAll();

    const [entry] = await readJsonl(join(resultDir, "operation-log.jsonl"));
    expect(entry.result).toEqual({
      status: "blocked",
      blocked_reason: "missing_client_control",
      error_message: null,
    });
  });

  it("records API logs and aggregates api-summary.json by phase, path, status, blocked capability, and step refs", async () => {
    const recorder = createOperationRecorder({
      resultDir,
      runId: "run-1",
      now: () => "2026-06-14T00:00:00.000Z",
    });

    const apiRef = recorder.recordApiCall({
      phase: "phase-1",
      source_step_id: "P1-05",
      method: "POST",
      url_origin: "validation-client-api",
      path_template: "/sessions/worldengine",
      path_redacted: "/sessions/worldengine",
      request_summary: {
        body_shape: ["session_name", "worldview"],
        public_input_lengths: { worldview: 58 },
        secrets_included: false,
        raw_prompt_included: false,
      },
      response_summary: {
        status_code: 201,
        body_shape: ["session", "world"],
        world_id: "world-1",
        error_class: null,
      },
      duration_ms: 123,
    });
    recorder.recordApiCall({
      phase: "phase-3",
      source_step_id: "P3-07",
      method: "GET",
      url_origin: "worldengine-public-api",
      path_template: "/agents/{agent_id}/memory/summary",
      request_summary: {
        body_shape: [],
        public_input_lengths: {},
        secrets_included: false,
        raw_prompt_included: false,
      },
      response_summary: {
        status_code: 404,
        body_shape: ["detail"],
        error_class: "missing_worldengine_capability",
      },
      duration_ms: 45,
    });
    await recorder.writeAll();

    expect(apiRef).toBe("api-log:0001");
    const apiEntries = await readJsonl(join(resultDir, "api-log.jsonl"));
    expect(apiEntries).toHaveLength(2);
    expect(apiEntries[0]).toMatchObject({
      api_ref: "api-log:0001",
      schema_version: "0.9.0",
      source_step_id: "P1-05",
      method: "POST",
      path_template: "/sessions/worldengine",
      response_summary: { status_code: 201 },
    });

    const summary = JSON.parse(await readFile(join(resultDir, "api-summary.json"), "utf-8"));
    expect(summary).toMatchObject({
      schema_version: "0.9.0",
      run_id: "run-1",
      request_count: 2,
      request_count_by_phase: {
        "phase-1": 1,
        "phase-3": 1,
      },
      request_count_by_method_path: {
        "POST /sessions/worldengine": 1,
        "GET /agents/{agent_id}/memory/summary": 1,
      },
      non_2xx_responses: [
        {
          api_ref: "api-log:0002",
          source_step_id: "P3-07",
          status_code: 404,
          path_template: "/agents/{agent_id}/memory/summary",
        },
      ],
      blocked_capability_calls: [
        {
          api_ref: "api-log:0002",
          source_step_id: "P3-07",
          error_class: "missing_worldengine_capability",
          path_template: "/agents/{agent_id}/memory/summary",
        },
      ],
      step_api_refs: {
        "P1-05": ["api-log:0001"],
        "P3-07": ["api-log:0002"],
      },
      redaction: {
        status: "pass",
        blocking_findings: [],
      },
    });
  });

  it("writes transcript sections and blocks forbidden markers before artifact write", async () => {
    const recorder = createOperationRecorder({ resultDir, runId: "run-1" });

    recorder.recordTranscript("Phase 1", [
      "Agent opened the session library.",
      "WorldEngine health check was blocked.",
    ]);
    await recorder.writeAll();

    const transcript = await readFile(join(resultDir, "transcript.md"), "utf-8");
    expect(transcript).toContain("## Phase 1");
    expect(transcript).toContain("- Agent opened the session library.");

    const findings = await scanForBlockingMarkers([
      {
        path: "unsafe.txt",
        content: "authorization: bearer abc",
      },
    ]);
    expect(findings).toEqual([
      {
        path: "unsafe.txt",
        marker: "authorization",
      },
    ]);
    expect(redactText("authorization: bearer abc")).toBe("[redacted]");
  });
});
