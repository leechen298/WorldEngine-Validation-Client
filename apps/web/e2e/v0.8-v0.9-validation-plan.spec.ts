import { promises as fs } from "node:fs";
import { dirname } from "node:path";
import { expect, test } from "@playwright/test";
import type { TestInfo } from "@playwright/test";

const apiBase = process.env.VALIDATION_CLIENT_API_BASE || "http://127.0.0.1:8765";
const scenario = process.env.VALIDATION_CLIENT_SCENARIO || "worldengine-full-lifecycle-autonomous";

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

test("v0.8 browser flow exports checker handoff artifacts", async ({ page, request }, testInfo) => {
  const health = await request.get(`${apiBase}/health/worldengine`);
  expect(health.ok()).toBeTruthy();
  const healthPayload = await health.json();
  await writeJson(testInfo.outputPath("worldengine-health.json"), healthPayload);
  expect(healthPayload.worldengine.capabilities.world_creation).toBe("available");

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

  const sessionsResponse = await request.get(`${apiBase}/sessions`);
  expect(sessionsResponse.ok()).toBeTruthy();
  const sessionsPayload = await sessionsResponse.json();
  const session = sessionsPayload.sessions.find((item: { session_name: string }) => item.session_name === sessionName);
  expect(session).toBeTruthy();

  const evidenceResponse = await request.get(`${apiBase}/sessions/${session.id}/evidence/bundle/manifest`);
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
