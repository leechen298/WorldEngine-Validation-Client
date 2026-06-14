import { promises as fs } from "node:fs";
import { dirname, join } from "node:path";
import type { RedactionFinding } from "./operationRecorder";

const SCHEMA_VERSION = "0.9.1";
const DEFAULT_SCENARIO = "complete-worldengine-validation-suite";
const VALID_STATUSES = new Set(["pass", "partial", "blocked", "fail"]);

const REQUIRED_ARTIFACTS = [
  "coverage-matrix.json",
  "command-matrix.md",
  "operation-log.jsonl",
  "api-log.jsonl",
  "api-summary.json",
  "capability-discovery.json",
  "world-creation-summary.json",
  "session-summary.json",
  "runtime-control-summary.json",
  "timeline-evidence.json",
  "direction-boundary-summary.json",
  "agent-evidence.json",
  "memory-continuity-summary.json",
  "inspection-evidence.json",
  "scorecard-input.json",
  "redaction-report.json",
  "console.log",
  "transcript.md",
  "second-agent-review.md",
  "screenshots/status.json",
  "compat/world-lifecycle-summary.json",
  "compat/diff-replay-summary.json",
  "compat/scorecard-summary.json",
  "compat/redaction-scan.json",
];

type SuiteStatus = "pass" | "partial" | "blocked" | "fail";
type PhaseStatus = SuiteStatus | "not_run";

interface WorldEngineSummary {
  reachable: boolean;
  manifest_seen: boolean;
  capabilities: Record<string, unknown>;
}

interface StepRefs {
  operation_log_ref?: string | null;
  api_refs?: string[];
  artifact_refs?: string[];
}

interface StepCoverage {
  phase: string;
  planned: boolean;
  executed: boolean;
  not_run: boolean;
  blocked: boolean;
  blocked_reason: string | null;
  operation_log_ref: string | null;
  api_refs: string[];
  artifact_refs: string[];
}

interface CommandRecord {
  command: string;
  status: "passed" | "failed" | "blocked" | "not_run";
  notes?: string;
}

interface CompleteSuiteResultOptions {
  resultDir: string;
  runId: string;
  scenario?: string;
  now?: () => string;
  redactionFindings?: RedactionFinding[];
}

interface WriteResultOptions {
  status_reason: string;
  worldengine: WorldEngineSummary;
}

interface WriteBlockedResultOptions extends WriteResultOptions {
  taxonomy: string;
  operationLog: unknown[];
  apiLog: Array<Record<string, any>>;
  transcriptLines: string[];
  consoleLines: string[];
  screenshotStatuses: Array<{ name: string; status: string; path?: string }>;
}

export function createCompleteSuiteResult(options: CompleteSuiteResultOptions) {
  const scenario = options.scenario ?? DEFAULT_SCENARIO;
  const now = options.now ?? (() => new Date().toISOString());
  const steps = new Map<string, StepCoverage>();
  const redactionFindings = options.redactionFindings ?? [];

  function markStepPlanned(stepId: string, phase: string) {
    const existing = steps.get(stepId);
    steps.set(stepId, {
      phase,
      planned: true,
      executed: existing?.executed ?? false,
      not_run: existing?.not_run ?? true,
      blocked: existing?.blocked ?? false,
      blocked_reason: existing?.blocked_reason ?? null,
      operation_log_ref: existing?.operation_log_ref ?? null,
      api_refs: existing?.api_refs ?? [],
      artifact_refs: existing?.artifact_refs ?? [],
    });
  }

  function markStepExecuted(stepId: string, refs: StepRefs = {}) {
    const step = requireStep(stepId);
    steps.set(stepId, {
      ...step,
      executed: true,
      not_run: false,
      operation_log_ref: refs.operation_log_ref ?? step.operation_log_ref,
      api_refs: refs.api_refs ?? step.api_refs,
      artifact_refs: refs.artifact_refs ?? step.artifact_refs,
    });
  }

  function markStepBlocked(stepId: string, reason: string, refs: StepRefs = {}) {
    const step = requireStep(stepId);
    steps.set(stepId, {
      ...step,
      executed: true,
      not_run: false,
      blocked: true,
      blocked_reason: reason,
      operation_log_ref: refs.operation_log_ref ?? step.operation_log_ref,
      api_refs: refs.api_refs ?? step.api_refs,
      artifact_refs: refs.artifact_refs ?? step.artifact_refs,
    });
  }

  async function writeCoverageMatrix() {
    await writeJson("coverage-matrix.json", {
      schema_version: SCHEMA_VERSION,
      run_id: options.runId,
      scenario,
      generated_at: now(),
      steps: Object.fromEntries([...steps.entries()].sort(([left], [right]) => left.localeCompare(right))),
    });
  }

  async function writeApiSummary(apiLog: Array<Record<string, any>> = []) {
    await writeJson("api-summary.json", buildApiSummary(options.runId, apiLog, redactionFindings));
  }

  async function writeResultJson(requestedStatus: SuiteStatus, resultOptions: WriteResultOptions) {
    if (!VALID_STATUSES.has(requestedStatus)) {
      throw new Error(`Unsupported result status: ${requestedStatus}`);
    }
    const missingArtifacts = requestedStatus === "pass" ? await missingRequiredArtifacts() : [];
    const redaction = redactionStatus();
    const status = finalStatus(requestedStatus, missingArtifacts, redaction.status);
    const statusReason =
      missingArtifacts.length > 0
        ? `${resultOptions.status_reason}; missing required artifacts: ${missingArtifacts.join(", ")}`
        : resultOptions.status_reason;

    await writeJson("result.json", {
      schema_version: SCHEMA_VERSION,
      run_id: options.runId,
      scenario,
      status,
      status_reason: statusReason,
      generated_at: now(),
      worldengine: resultOptions.worldengine,
      phases: buildPhaseResults(),
      redaction,
      artifacts: await artifactIndex(),
    });
  }

  async function writeCommandMatrix(commands: CommandRecord[] = []) {
    const lines = ["# Command Matrix", "", "| Command | Status | Notes |", "| --- | --- | --- |"];
    for (const command of commands) {
      lines.push(`| \`${command.command}\` | ${command.status} | ${command.notes ?? ""} |`);
    }
    if (commands.length === 0) {
      lines.push("| not_run | not_run | no commands recorded yet |");
    }
    await writeText("command-matrix.md", `${lines.join("\n")}\n`);
  }

  async function writeCompatibilityArtifacts(status: SuiteStatus = "blocked") {
    await writeJson("compat/world-lifecycle-summary.json", placeholderArtifact("world-lifecycle-summary.json", status));
    await writeJson("compat/diff-replay-summary.json", placeholderArtifact("diff-replay-summary.json", status));
    await writeJson("compat/scorecard-summary.json", placeholderArtifact("scorecard-summary.json", status));
    await writeJson("compat/redaction-scan.json", {
      schema_version: SCHEMA_VERSION,
      scenario,
      status: redactionStatus().status,
      blocking_findings: redactionFindings,
    });
  }

  async function writeBlockedResult(blockedOptions: WriteBlockedResultOptions) {
    await writeCoverageMatrix();
    await writeJsonl("operation-log.jsonl", blockedOptions.operationLog);
    await writeJsonl("api-log.jsonl", blockedOptions.apiLog);
    await writeApiSummary(blockedOptions.apiLog);
    await writeJson("capability-discovery.json", {
      schema_version: SCHEMA_VERSION,
      scenario,
      status: "blocked",
      taxonomy: blockedOptions.taxonomy,
      worldengine: blockedOptions.worldengine,
    });
    await writeJson("redaction-report.json", {
      schema_version: SCHEMA_VERSION,
      scenario,
      ...redactionStatus(),
    });
    await writeText("console.log", `${blockedOptions.consoleLines.join("\n")}\n`);
    await writeText(
      "transcript.md",
      [
        "# Agent Autonomous Validation Transcript",
        "",
        "## Blocked Result",
        ...blockedOptions.transcriptLines.map((line) => `- ${line}`),
        "",
      ].join("\n"),
    );
    await writeJson("screenshots/status.json", {
      schema_version: SCHEMA_VERSION,
      screenshots: blockedOptions.screenshotStatuses,
    });
    await writeCommandMatrix([
      {
        command: "complete-worldengine-validation-suite",
        status: "blocked",
        notes: blockedOptions.taxonomy,
      },
    ]);
    await writeBlockedPlaceholders(blockedOptions.taxonomy);
    await writeCompatibilityArtifacts("blocked");
    await writeResultJson("blocked", blockedOptions);
  }

  function requireStep(stepId: string): StepCoverage {
    const step = steps.get(stepId);
    if (!step) {
      throw new Error(`Step ${stepId} must be planned before marking execution`);
    }
    return step;
  }

  async function writeJson(relativePath: string, payload: unknown) {
    await writeText(relativePath, `${JSON.stringify(payload, null, 2)}\n`);
  }

  async function writeJsonl(relativePath: string, payload: unknown[]) {
    await writeText(relativePath, payload.length === 0 ? "" : `${payload.map((item) => JSON.stringify(item)).join("\n")}\n`);
  }

  async function writeText(relativePath: string, content: string) {
    const fullPath = join(options.resultDir, relativePath);
    await fs.mkdir(dirname(fullPath), { recursive: true });
    await fs.writeFile(fullPath, content);
  }

  async function writeBlockedPlaceholders(taxonomy: string) {
    for (const artifact of [
      "world-creation-summary.json",
      "session-summary.json",
      "runtime-control-summary.json",
      "timeline-evidence.json",
      "direction-boundary-summary.json",
      "agent-evidence.json",
      "memory-continuity-summary.json",
      "inspection-evidence.json",
      "scorecard-input.json",
    ]) {
      await writeJson(artifact, placeholderArtifact(artifact, "blocked", taxonomy));
    }
    await writeText("second-agent-review.md", `# Second Agent Review\n\n- Status: blocked\n- Reason: ${taxonomy}\n`);
  }

  async function missingRequiredArtifacts(): Promise<string[]> {
    const missing = [];
    for (const artifact of REQUIRED_ARTIFACTS) {
      try {
        await fs.access(join(options.resultDir, artifact));
      } catch {
        missing.push(artifact);
      }
    }
    return missing;
  }

  async function artifactIndex() {
    const artifacts = [];
    for (const artifact of REQUIRED_ARTIFACTS) {
      let exists = true;
      try {
        await fs.access(join(options.resultDir, artifact));
      } catch {
        exists = false;
      }
      artifacts.push({
        path: artifact,
        required: true,
        status: exists ? "present" : "missing",
      });
    }
    return artifacts;
  }

  function buildPhaseResults() {
    const byPhase = new Map<string, StepCoverage[]>();
    for (const step of steps.values()) {
      byPhase.set(step.phase, [...(byPhase.get(step.phase) ?? []), step]);
    }
    return [...byPhase.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([phase, phaseSteps]) => {
        const executedSteps = phaseSteps.filter((step) => !step.not_run).map((step) => stepIdFor(step));
        const blockedStep = phaseSteps.find((step) => step.blocked);
        return {
          phase,
          status: phaseStatus(phaseSteps),
          executed_steps: executedSteps,
          blocked_reason: blockedStep?.blocked_reason ?? null,
          pass_source: "none",
        };
      });
  }

  function stepIdFor(targetStep: StepCoverage): string {
    for (const [stepId, step] of steps.entries()) {
      if (step === targetStep) {
        return stepId;
      }
    }
    throw new Error("Unknown step coverage entry");
  }

  function phaseStatus(phaseSteps: StepCoverage[]): PhaseStatus {
    if (phaseSteps.some((step) => step.blocked)) {
      return "blocked";
    }
    if (phaseSteps.some((step) => step.executed)) {
      return "pass";
    }
    return "not_run";
  }

  function redactionStatus() {
    return {
      status: redactionFindings.length === 0 ? "pass" : "fail",
      blocking_findings: redactionFindings,
    };
  }

  return {
    markStepPlanned,
    markStepExecuted,
    markStepBlocked,
    writeCoverageMatrix,
    writeApiSummary,
    writeResultJson,
    writeCommandMatrix,
    writeCompatibilityArtifacts,
    writeBlockedResult,
  };
}

function buildApiSummary(runId: string, apiLog: Array<Record<string, any>>, findings: RedactionFinding[]) {
  const requestCountByPhase: Record<string, number> = {};
  const non2xxResponses = [];
  const blockedCapabilityCalls = [];
  const stepApiRefs: Record<string, string[]> = {};

  for (const item of apiLog) {
    const phase = item.phase ?? "unknown";
    requestCountByPhase[phase] = (requestCountByPhase[phase] ?? 0) + 1;
    const sourceStepId = item.source_step_id ?? "unknown";
    if (item.api_ref) {
      stepApiRefs[sourceStepId] = [...(stepApiRefs[sourceStepId] ?? []), item.api_ref];
    }
    const statusCode = item.response_summary?.status_code;
    if (typeof statusCode === "number" && (statusCode < 200 || statusCode >= 300)) {
      non2xxResponses.push({
        api_ref: item.api_ref ?? null,
        source_step_id: sourceStepId,
        status_code: statusCode,
      });
    }
    const errorClass = item.response_summary?.error_class;
    if (typeof errorClass === "string" && errorClass.includes("capability")) {
      blockedCapabilityCalls.push({
        api_ref: item.api_ref ?? null,
        source_step_id: sourceStepId,
        error_class: errorClass,
      });
    }
  }

  return {
    schema_version: SCHEMA_VERSION,
    run_id: runId,
    request_count: apiLog.length,
    request_count_by_phase: requestCountByPhase,
    non_2xx_responses: non2xxResponses,
    blocked_capability_calls: blockedCapabilityCalls,
    step_api_refs: stepApiRefs,
    redaction: {
      status: findings.length === 0 ? "pass" : "fail",
      blocking_findings: findings,
    },
  };
}

function finalStatus(requestedStatus: SuiteStatus, missingArtifacts: string[], redactionStatus: string): SuiteStatus {
  if (redactionStatus === "fail") {
    return "fail";
  }
  if (requestedStatus === "pass" && missingArtifacts.length > 0) {
    return "partial";
  }
  return requestedStatus;
}

function placeholderArtifact(name: string, status: SuiteStatus, reason?: string) {
  return {
    schema_version: SCHEMA_VERSION,
    artifact: name,
    status,
    reason: reason ?? null,
  };
}
