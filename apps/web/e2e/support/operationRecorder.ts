import { promises as fs } from "node:fs";
import { dirname, join } from "node:path";

const SCHEMA_VERSION = "0.9.0";

const BLOCKING_MARKERS = [
  "api key",
  "authorization",
  "credential",
  "token",
  "password",
  "secret",
  "raw prompt",
  "raw provider request",
  "raw provider response",
  "private memory",
  "private goal",
  "raw thought",
  "chain-of-thought",
  "hidden context",
  "worldengine private path",
];

const OPERATION_KINDS = new Set([
  "page_open",
  "click",
  "fill",
  "select",
  "keyboard",
  "wait_for_visible",
  "wait_for_response",
  "download",
  "screenshot",
  "observe",
  "phase_verdict",
  "blocked",
]);

type Phase = "phase-1" | "phase-2" | "phase-3" | "phase-4" | string;
type OperationStatus = "executed" | "blocked" | "failed" | "not_run";

export interface OperationRecorderOptions {
  resultDir: string;
  runId: string;
  actor?: string;
  now?: () => string;
}

export interface OperationTarget {
  page?: string | null;
  role?: string | null;
  label?: string | null;
  test_id?: string | null;
  selector?: string | null;
}

export interface OperationInput {
  text_redacted?: string | null;
  value_redacted?: string | null;
  value_length?: number | null;
  source?: "user_public_input" | "test_control" | string | null;
}

export interface OperationSnapshot {
  url?: string | null;
  visible_text_summary?: string | null;
  screenshot?: string | null;
}

export interface OperationResult {
  status: OperationStatus;
  blocked_reason?: string | null;
  error_message?: string | null;
}

export interface OperationRecordInput {
  step_id: string;
  phase: Phase;
  operation_kind: string;
  target?: OperationTarget;
  input?: OperationInput;
  before?: OperationSnapshot;
  after?: OperationSnapshot;
  api_refs?: string[];
  artifact_refs?: string[];
  result: OperationResult;
}

export interface ApiSummaryShape {
  body_shape: string[];
  public_input_lengths: Record<string, number>;
  secrets_included: boolean;
  raw_prompt_included: boolean;
  direct_harvest?: boolean;
  redaction_flags?: Record<string, boolean>;
}

export interface ApiResponseSummary {
  status_code: number;
  body_shape: string[];
  world_id?: string | null;
  error_class?: string | null;
}

export interface ApiRecordInput {
  phase: Phase;
  source_step_id: string;
  method: string;
  url_origin: "validation-client-api" | "worldengine-public-api" | string;
  path_template: string;
  path_redacted?: string;
  request_summary: ApiSummaryShape;
  response_summary: ApiResponseSummary;
  duration_ms: number;
}

export interface RedactionFinding {
  path: string;
  marker: string;
}

interface FileCandidate {
  path: string;
  content: string;
}

interface OperationRecord extends Required<Omit<OperationRecordInput, "target" | "input" | "before" | "after">> {
  schema_version: string;
  run_id: string;
  operation_ref: string;
  actor: string;
  target: Required<OperationTarget>;
  input: Required<OperationInput>;
  before: Required<OperationSnapshot>;
  after: Required<OperationSnapshot>;
  timestamp: string;
}

interface ApiRecord extends ApiRecordInput {
  schema_version: string;
  run_id: string;
  api_ref: string;
  method: string;
  path_redacted: string;
  timestamp: string;
}

export function redactText(value: string | null | undefined): string | null {
  if (value == null) {
    return null;
  }
  return hasBlockingMarker(value) ? "[redacted]" : value;
}

export async function scanForBlockingMarkers(files: FileCandidate[]): Promise<RedactionFinding[]> {
  const findings: RedactionFinding[] = [];
  for (const file of files) {
    for (const marker of BLOCKING_MARKERS) {
      if (markerPattern(marker).test(file.content)) {
        findings.push({ path: file.path, marker });
      }
    }
  }
  return findings;
}

export function createOperationRecorder(options: OperationRecorderOptions) {
  const actor = options.actor ?? "codex-agent";
  const now = options.now ?? (() => new Date().toISOString());
  const operations: OperationRecord[] = [];
  const apiCalls: ApiRecord[] = [];
  const transcriptSections: Array<{ section: string; lines: string[] }> = [];

  function recordOperation(input: OperationRecordInput): string {
    if (!OPERATION_KINDS.has(input.operation_kind)) {
      throw new Error(`Unsupported operation_kind: ${input.operation_kind}`);
    }
    const operationRef = formatRef("operation-log", operations.length + 1);
    operations.push({
      schema_version: SCHEMA_VERSION,
      run_id: options.runId,
      operation_ref: operationRef,
      step_id: input.step_id,
      phase: input.phase,
      actor,
      operation_kind: input.operation_kind,
      target: normalizeTarget(input.target),
      input: normalizeOperationInput(input.input),
      before: normalizeSnapshot(input.before),
      after: normalizeSnapshot(input.after),
      api_refs: input.api_refs ?? [],
      artifact_refs: input.artifact_refs ?? [],
      result: normalizeResult(input.result),
      timestamp: now(),
    });
    return operationRef;
  }

  function recordApiCall(input: ApiRecordInput): string {
    const apiRef = formatRef("api-log", apiCalls.length + 1);
    apiCalls.push({
      schema_version: SCHEMA_VERSION,
      run_id: options.runId,
      api_ref: apiRef,
      phase: input.phase,
      source_step_id: input.source_step_id,
      method: input.method.toUpperCase(),
      url_origin: input.url_origin,
      path_template: input.path_template,
      path_redacted: input.path_redacted ?? input.path_template,
      request_summary: input.request_summary,
      response_summary: input.response_summary,
      duration_ms: input.duration_ms,
      timestamp: now(),
    });
    return apiRef;
  }

  async function recordScreenshot(
    stepId: string,
    phase: Phase,
    page: { screenshot: (options: { path: string; fullPage?: boolean }) => Promise<unknown> },
    name: string,
  ): Promise<string> {
    const screenshotRef = join("screenshots", name);
    await page.screenshot({ path: join(options.resultDir, screenshotRef), fullPage: true });
    recordOperation({
      step_id: stepId,
      phase,
      operation_kind: "screenshot",
      target: { page: "Validation Client", label: name },
      artifact_refs: [screenshotRef],
      result: { status: "executed" },
    });
    return screenshotRef;
  }

  function recordTranscript(section: string, lines: string[]) {
    transcriptSections.push({ section, lines });
  }

  async function writeAll() {
    const operationLog = toJsonl(operations);
    const apiLog = toJsonl(apiCalls);
    const apiSummary = JSON.stringify(buildApiSummary(options.runId, apiCalls, []), null, 2);
    const transcript = buildTranscript(transcriptSections);
    const findings = await scanForBlockingMarkers([
      { path: "operation-log.jsonl", content: operationLog },
      { path: "api-log.jsonl", content: apiLog },
      { path: "api-summary.json", content: apiSummary },
      { path: "transcript.md", content: transcript },
    ]);
    const finalApiSummary = JSON.stringify(buildApiSummary(options.runId, apiCalls, findings), null, 2);

    await writeFile(join(options.resultDir, "operation-log.jsonl"), operationLog);
    await writeFile(join(options.resultDir, "api-log.jsonl"), apiLog);
    await writeFile(join(options.resultDir, "api-summary.json"), `${finalApiSummary}\n`);
    await writeFile(join(options.resultDir, "transcript.md"), transcript);
  }

  return {
    recordOperation,
    recordApiCall,
    recordScreenshot,
    recordTranscript,
    writeTranscript: recordTranscript,
    getOperationLog: () => operations,
    getApiLog: () => apiCalls,
    writeAll,
  };
}

function normalizeTarget(target?: OperationTarget): Required<OperationTarget> {
  return {
    page: target?.page ?? null,
    role: target?.role ?? null,
    label: target?.label ?? null,
    test_id: target?.test_id ?? null,
    selector: target?.selector ?? null,
  };
}

function normalizeOperationInput(input?: OperationInput): Required<OperationInput> {
  return {
    text_redacted: redactText(input?.text_redacted) ?? null,
    value_redacted: redactText(input?.value_redacted) ?? null,
    value_length: input?.value_length ?? null,
    source: input?.source ?? null,
  };
}

function normalizeSnapshot(snapshot?: OperationSnapshot): Required<OperationSnapshot> {
  return {
    url: snapshot?.url ?? null,
    visible_text_summary: snapshot?.visible_text_summary ?? null,
    screenshot: snapshot?.screenshot ?? null,
  };
}

function normalizeResult(result: OperationResult): Required<OperationResult> {
  return {
    status: result.status,
    blocked_reason: result.blocked_reason ?? null,
    error_message: result.error_message ?? null,
  };
}

function buildApiSummary(runId: string, apiCalls: ApiRecord[], findings: RedactionFinding[]) {
  const requestCountByPhase: Record<string, number> = {};
  const requestCountByMethodPath: Record<string, number> = {};
  const stepApiRefs: Record<string, string[]> = {};
  const non2xxResponses = [];
  const blockedCapabilityCalls = [];
  let directHarvestCount = 0;

  for (const call of apiCalls) {
    requestCountByPhase[call.phase] = (requestCountByPhase[call.phase] ?? 0) + 1;
    const methodPath = `${call.method} ${call.path_template}`;
    requestCountByMethodPath[methodPath] = (requestCountByMethodPath[methodPath] ?? 0) + 1;
    stepApiRefs[call.source_step_id] = [...(stepApiRefs[call.source_step_id] ?? []), call.api_ref];
    if (call.request_summary.direct_harvest) {
      directHarvestCount += 1;
    }
    if (call.response_summary.status_code < 200 || call.response_summary.status_code >= 300) {
      non2xxResponses.push({
        api_ref: call.api_ref,
        source_step_id: call.source_step_id,
        status_code: call.response_summary.status_code,
        path_template: call.path_template,
      });
    }
    if (call.response_summary.error_class?.includes("capability")) {
      blockedCapabilityCalls.push({
        api_ref: call.api_ref,
        source_step_id: call.source_step_id,
        error_class: call.response_summary.error_class,
        path_template: call.path_template,
      });
    }
  }

  return {
    schema_version: SCHEMA_VERSION,
    run_id: runId,
    request_count: apiCalls.length,
    request_count_by_phase: requestCountByPhase,
    request_count_by_method_path: requestCountByMethodPath,
    non_2xx_responses: non2xxResponses,
    blocked_capability_calls: blockedCapabilityCalls,
    direct_api_harvest_count: directHarvestCount,
    step_api_refs: stepApiRefs,
    redaction: {
      status: findings.length === 0 ? "pass" : "fail",
      blocking_findings: findings,
    },
  };
}

function buildTranscript(sections: Array<{ section: string; lines: string[] }>): string {
  const lines = ["# Agent Autonomous Validation Transcript", ""];
  for (const section of sections) {
    lines.push(`## ${section.section}`);
    for (const line of section.lines) {
      lines.push(`- ${line}`);
    }
    lines.push("");
  }
  return lines.join("\n");
}

function toJsonl(records: unknown[]): string {
  if (records.length === 0) {
    return "";
  }
  return `${records.map((record) => JSON.stringify(record)).join("\n")}\n`;
}

async function writeFile(path: string, content: string) {
  await fs.mkdir(dirname(path), { recursive: true });
  await fs.writeFile(path, content);
}

function formatRef(prefix: string, index: number): string {
  return `${prefix}:${String(index).padStart(4, "0")}`;
}

function hasBlockingMarker(value: string): boolean {
  return BLOCKING_MARKERS.some((marker) => markerPattern(marker).test(value));
}

function markerPattern(marker: string): RegExp {
  const escaped = marker.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`, "i");
}
