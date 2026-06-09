import { promises as fs } from "node:fs";
import { dirname } from "node:path";
import { expect, test } from "@playwright/test";
import type { TestInfo } from "@playwright/test";

const apiBase = process.env.VALIDATION_CLIENT_API_BASE || "http://127.0.0.1:8765";
const scenario = process.env.VALIDATION_CLIENT_SCENARIO || "worldengine-full-lifecycle-autonomous";
const BLOCKED_HANDOFF_ARTIFACTS = [
  { name: "manifest.json", producer: "validation_client", status: "blocked" },
  { name: "result.json", producer: "validation_client", status: "blocked" },
  { name: "redaction-scan.json", producer: "validation_client", status: "pass" },
  { name: "scorecard-summary.json", producer: "worldengine_checker", status: "blocked" },
  { name: "operation-log.jsonl", producer: "validation_client", status: "blocked" },
  { name: "api-summary.json", producer: "validation_client", status: "blocked" },
  { name: "worldengine-health.json", producer: "validation_client", status: "blocked" },
];

async function writeJson(path: string, payload: unknown) {
  await fs.mkdir(dirname(path), { recursive: true });
  await fs.writeFile(path, JSON.stringify(payload, null, 2));
}

function toJsonl(payload: unknown): string {
  if (Array.isArray(payload)) {
    return payload.map((item) => JSON.stringify(item)).join("\n");
  }
  return `${JSON.stringify(payload)}\n`;
}

async function writeHandoffArtifact(testInfo: TestInfo, name: string, payload: unknown) {
  const artifactPath = testInfo.outputPath("checker-handoff", name.endsWith("/") ? `${name}status.json` : name);
  await fs.mkdir(dirname(artifactPath), { recursive: true });
  if (name.endsWith(".jsonl")) {
    await fs.writeFile(artifactPath, toJsonl(payload));
    return;
  }
  if (name.endsWith(".md") || name.endsWith(".log")) {
    await fs.writeFile(artifactPath, typeof payload === "string" ? payload : JSON.stringify(payload, null, 2));
    return;
  }
  await writeJson(artifactPath, payload);
}

function classifyWorldEngineBlocker(healthPayload: any): string {
  const worldengine = healthPayload.worldengine || {};
  if (!worldengine.reachable) {
    return "WorldEngine public surface is not reachable";
  }
  if (!worldengine.openapi) {
    return "WorldEngine OpenAPI is unavailable";
  }
  if (worldengine.capabilities?.world_creation !== "available") {
    return "WorldEngine world creation public surface is unavailable";
  }
  return "WorldEngine public validation surface is unavailable";
}

async function writeBlockedHandoff(testInfo: TestInfo, healthPayload: any) {
  const unsupportedItems = [classifyWorldEngineBlocker(healthPayload)];
  const redactionStatus = { status: "pass", blocking_flags: [] };
  const manifest = {
    schema_version: "0.8.0",
    bundle_id: `v0.8-blocked-${Date.now()}`,
    scenario,
    result_status: "blocked",
    client_role: "display_export_only",
    provider_owner: "worldengine",
    evaluator_role: "worldengine_checker_or_second_agent_review",
    redaction_status: redactionStatus,
    artifact_index: BLOCKED_HANDOFF_ARTIFACTS.map((artifact) => ({
      name: artifact.name,
      path: artifact.name,
      required: true,
      displayable: !artifact.name.endsWith(".jsonl"),
      exportable: true,
      producer: artifact.producer,
      schema_version: "0.8.0",
      status: artifact.status,
      redaction_status: redactionStatus.status,
    })),
    checker_contract: {
      scenario,
      status_values: ["pass", "fail", "blocked", "not_run"],
      pass_source: "worldengine_checker_or_second_agent_review",
    },
    unsupported_items: unsupportedItems,
  };
  await writeHandoffArtifact(testInfo, "manifest.json", manifest);
  await writeHandoffArtifact(testInfo, "result.json", {
    schema_version: "0.8.0",
    scenario,
    status: "blocked",
    client_role: "display_export_only",
    provider_owner: "worldengine",
    evaluator_role: "worldengine_checker_or_second_agent_review",
    unsupported_items: manifest.unsupported_items,
    checker_contract: manifest.checker_contract,
    redaction: manifest.redaction_status,
  });
  await writeHandoffArtifact(testInfo, "worldengine-health.json", healthPayload);
  await writeHandoffArtifact(testInfo, "redaction-scan.json", {
    schema_version: "0.8.0",
    scenario,
    status: "pass",
    blocking_flags: [],
  });
  await writeHandoffArtifact(testInfo, "scorecard-summary.json", {
    schema_version: "0.8.0",
    scenario,
    status: "blocked",
    verdict_source: "worldengine_checker",
    score_items: [],
    critical_failures: manifest.unsupported_items,
    unverified_items: manifest.unsupported_items,
    final_status: "blocked",
  });
  await writeHandoffArtifact(testInfo, "operation-log.jsonl", []);
  await writeHandoffArtifact(testInfo, "api-summary.json", {
    schema_version: "0.8.0",
    scenario,
    status: "blocked",
    api_trace_count: 0,
    redaction: manifest.redaction_status,
  });
}

test("v0.8 browser flow exports checker handoff artifacts", async ({ page, request }, testInfo) => {
  const health = await request.get(`${apiBase}/health/worldengine`);
  expect(health.ok()).toBeTruthy();
  const healthPayload = await health.json();
  await writeJson(testInfo.outputPath("worldengine-health.json"), healthPayload);
  if (healthPayload.worldengine.capabilities.world_creation !== "available") {
    testInfo.annotations.push({
      type: "blocked",
      description: "WorldEngine public surface is not reachable; blocked handoff artifacts were exported.",
    });
    await writeBlockedHandoff(testInfo, healthPayload);
    const blockedManifest = JSON.parse(
      await fs.readFile(testInfo.outputPath("checker-handoff", "manifest.json"), "utf-8"),
    );
    const indexedArtifacts = blockedManifest.artifact_index.map((item: { name: string }) => item.name).sort();
    expect(indexedArtifacts).toEqual(
      [
        "api-summary.json",
        "manifest.json",
        "operation-log.jsonl",
        "redaction-scan.json",
        "result.json",
        "scorecard-summary.json",
        "worldengine-health.json",
      ].sort(),
    );
    return;
  }

  const runSlug = Date.now();
  const sessionName = `v0.8 E2E ${runSlug}`;
  const branchName = `e2e-branch-${runSlug}`;

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "会话库" })).toBeVisible();
  await expect(page.getByText("status: ok")).toBeVisible();

  await page.getByRole("textbox", { name: "Session 名称" }).fill(sessionName);
  await page.getByRole("textbox", { name: "世界观" }).fill("一个公开可观察的海港像素世界，有居民、道路和市场。");
  await page.getByRole("button", { name: "创建世界" }).click();

  await expect(page.getByRole("heading", { name: "运行控制" })).toBeVisible();
  await expect(page.getByText("公开像素地图")).toBeVisible();
  await expect(page.getByRole("heading", { name: "公开状态摘要" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "World Log" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Agent Life Log" })).toBeVisible();
  await page.getByLabel("验证场景").selectOption(scenario);
  await expect(page.getByText(`v0.8 scenario：${scenario}`)).toBeVisible();

  await page.getByLabel("运行 tick 数").fill("7");
  await page.getByRole("button", { name: "Run 7 ticks" }).click();
  await expect(page.getByText("状态：running")).toBeVisible();
  await page.getByRole("button", { name: "Pause run" }).click();
  await expect(page.getByText("状态：paused")).toBeVisible();
  await page.getByRole("button", { name: "Resume run" }).click();
  await expect(page.getByText("状态：running")).toBeVisible();
  await page.getByRole("button", { name: "Single Tick" }).click();

  await page.getByLabel("高层方向 / 外部世界趋势").fill("让居民更关注市场合作，但不要直接投放物品。");
  await page.getByRole("button", { name: "提交引导" }).click();
  await expect(page.getByText(/状态：accepted|状态：pending|状态：applied/)).toBeVisible();

  await page.getByLabel("目标 tick").evaluate((node) => {
    const input = node as HTMLInputElement;
    input.value = "0";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });

  await page.getByLabel("新 branch 名称").fill(branchName);
  await page.getByRole("button", { name: "从当前 commit point 创建 branch" }).click();
  await expect(page.getByRole("button", { name: `切换到 branch ${branchName}` })).toBeVisible();

  const screenshotPath = testInfo.outputPath("runtime-console.png");
  await page.screenshot({ path: screenshotPath, fullPage: true });

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "下载 evidence bundle" }).click();
  const download = await downloadPromise;
  await download.saveAs(testInfo.outputPath("evidence-bundle.json"));
  await expect(page.getByText(/已下载：evidence-bundle-/)).toBeVisible();

  const handoffDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "下载 checker handoff" }).click();
  const handoffDownload = await handoffDownloadPromise;
  await handoffDownload.saveAs(testInfo.outputPath("checker-handoff.json"));
  await expect(page.getByText(/已下载：evidence-artifacts-/)).toBeVisible();

  const sessionsResponse = await request.get(`${apiBase}/sessions`);
  expect(sessionsResponse.ok()).toBeTruthy();
  const sessionsPayload = await sessionsResponse.json();
  const session = sessionsPayload.sessions.find((item: { session_name: string }) => item.session_name === sessionName);
  expect(session).toBeTruthy();

  const evidenceResponse = await request.get(`${apiBase}/sessions/${session.id}/evidence/bundle/manifest?scenario=${scenario}`);
  expect(evidenceResponse.ok()).toBeTruthy();
  const evidencePayload = await evidenceResponse.json();
  await fs.writeFile(testInfo.outputPath("evidence-bundle-manifest.json"), JSON.stringify(evidencePayload, null, 2));
  await writeHandoffArtifact(testInfo, "manifest.json", evidencePayload.manifest);

  await expect(page.getByText(`v0.8 scenario：${scenario}`)).toBeVisible();
  await expect(page.getByText(/结果状态：pass|结果状态：fail|结果状态：blocked|结果状态：not_run|结果状态：unknown/)).toBeVisible();
  await expect(page.getByText(/Redaction scan：pass|Redaction scan：fail|Redaction scan：not_run/)).toBeVisible();

  const runId = evidencePayload.manifest.latest_validation_run_id;
  expect(runId).toBeTruthy();

  const operationLogResponse = await request.get(`${apiBase}/validation-runs/${runId}/operation-log.jsonl`);
  expect(operationLogResponse.ok()).toBeTruthy();
  await fs.writeFile(testInfo.outputPath("agent-run.jsonl"), await operationLogResponse.text());

  const apiSummaryResponse = await request.get(`${apiBase}/validation-runs/${runId}/api-summary`);
  expect(apiSummaryResponse.ok()).toBeTruthy();
  await fs.writeFile(testInfo.outputPath("api-summary.json"), JSON.stringify(await apiSummaryResponse.json(), null, 2));

  const artifactsResponse = await request.get(`${apiBase}/sessions/${session.id}/evidence/bundle/artifacts?scenario=${scenario}`);
  expect(artifactsResponse.ok()).toBeTruthy();
  const artifacts = await artifactsResponse.json();
  for (const [name, payload] of Object.entries(artifacts)) {
    await writeHandoffArtifact(testInfo, name, payload);
  }
});

test("blocked handoff classifies reachable discovery gaps", async ({}, testInfo) => {
  await writeBlockedHandoff(testInfo, {
    status: "degraded",
    worldengine: {
      reachable: true,
      health: { status: "ok" },
      manifest: null,
      openapi: null,
      capabilities: {
        world_creation: "unknown",
        v0_9_validation: "not_run",
      },
      errors: ["openapi: 404"],
    },
  });

  const result = JSON.parse(await fs.readFile(testInfo.outputPath("checker-handoff", "result.json"), "utf-8"));
  expect(result.unsupported_items).toContain("WorldEngine OpenAPI is unavailable");
  expect(result.unsupported_items).not.toContain("WorldEngine public surface is not reachable");
});
