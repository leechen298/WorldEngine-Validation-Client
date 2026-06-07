# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: v0.8-v0.9-validation-plan.spec.ts >> v0.8 browser flow exports checker handoff artifacts
- Location: e2e/v0.8-v0.9-validation-plan.spec.ts:35:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "available"
Received: "unknown"
```

# Test source

```ts
  1   | import { promises as fs } from "node:fs";
  2   | import { dirname } from "node:path";
  3   | import { expect, test } from "@playwright/test";
  4   | import type { TestInfo } from "@playwright/test";
  5   | 
  6   | const apiBase = process.env.VALIDATION_CLIENT_API_BASE || "http://127.0.0.1:8765";
  7   | const scenario = process.env.VALIDATION_CLIENT_SCENARIO || "worldengine-full-lifecycle-autonomous";
  8   | 
  9   | async function writeJson(path: string, payload: unknown) {
  10  |   await fs.mkdir(dirname(path), { recursive: true });
  11  |   await fs.writeFile(path, JSON.stringify(payload, null, 2));
  12  | }
  13  | 
  14  | function toJsonl(payload: unknown): string {
  15  |   if (Array.isArray(payload)) {
  16  |     return payload.map((item) => JSON.stringify(item)).join("\n");
  17  |   }
  18  |   return `${JSON.stringify(payload)}\n`;
  19  | }
  20  | 
  21  | async function writeHandoffArtifact(testInfo: TestInfo, name: string, payload: unknown) {
  22  |   const artifactPath = testInfo.outputPath("checker-handoff", name.endsWith("/") ? `${name}status.json` : name);
  23  |   await fs.mkdir(dirname(artifactPath), { recursive: true });
  24  |   if (name.endsWith(".jsonl")) {
  25  |     await fs.writeFile(artifactPath, toJsonl(payload));
  26  |     return;
  27  |   }
  28  |   if (name.endsWith(".md") || name.endsWith(".log")) {
  29  |     await fs.writeFile(artifactPath, typeof payload === "string" ? payload : JSON.stringify(payload, null, 2));
  30  |     return;
  31  |   }
  32  |   await writeJson(artifactPath, payload);
  33  | }
  34  | 
  35  | test("v0.8 browser flow exports checker handoff artifacts", async ({ page, request }, testInfo) => {
  36  |   const health = await request.get(`${apiBase}/health/worldengine`);
  37  |   expect(health.ok()).toBeTruthy();
  38  |   const healthPayload = await health.json();
  39  |   await writeJson(testInfo.outputPath("worldengine-health.json"), healthPayload);
> 40  |   expect(healthPayload.worldengine.capabilities.world_creation).toBe("available");
      |                                                                 ^ Error: expect(received).toBe(expected) // Object.is equality
  41  | 
  42  |   const runSlug = Date.now();
  43  |   const sessionName = `v0.8 E2E ${runSlug}`;
  44  |   const branchName = `e2e-branch-${runSlug}`;
  45  | 
  46  |   await page.goto("/");
  47  |   await expect(page.getByRole("heading", { name: "会话库" })).toBeVisible();
  48  |   await expect(page.getByText("status: ok")).toBeVisible();
  49  | 
  50  |   await page.getByRole("textbox", { name: "Session 名称" }).fill(sessionName);
  51  |   await page.getByRole("textbox", { name: "世界观" }).fill("一个公开可观察的海港像素世界，有居民、道路和市场。");
  52  |   await page.getByRole("button", { name: "创建世界" }).click();
  53  | 
  54  |   await expect(page.getByRole("heading", { name: "运行控制" })).toBeVisible();
  55  |   await expect(page.getByText("公开像素地图")).toBeVisible();
  56  |   await expect(page.getByRole("heading", { name: "公开状态摘要" })).toBeVisible();
  57  |   await expect(page.getByRole("heading", { name: "World Log" })).toBeVisible();
  58  |   await expect(page.getByRole("heading", { name: "Agent Life Log" })).toBeVisible();
  59  | 
  60  |   await page.getByLabel("运行 tick 数").fill("7");
  61  |   await page.getByRole("button", { name: "Run 7 ticks" }).click();
  62  |   await expect(page.getByText("状态：running")).toBeVisible();
  63  |   await page.getByRole("button", { name: "Pause run" }).click();
  64  |   await expect(page.getByText("状态：paused")).toBeVisible();
  65  |   await page.getByRole("button", { name: "Resume run" }).click();
  66  |   await expect(page.getByText("状态：running")).toBeVisible();
  67  |   await page.getByRole("button", { name: "Single Tick" }).click();
  68  | 
  69  |   await page.getByLabel("高层方向 / 外部世界趋势").fill("让居民更关注市场合作，但不要直接投放物品。");
  70  |   await page.getByRole("button", { name: "提交引导" }).click();
  71  |   await expect(page.getByText(/状态：accepted|状态：pending|状态：applied/)).toBeVisible();
  72  | 
  73  |   await page.getByLabel("目标 tick").evaluate((node) => {
  74  |     const input = node as HTMLInputElement;
  75  |     input.value = "0";
  76  |     input.dispatchEvent(new Event("input", { bubbles: true }));
  77  |     input.dispatchEvent(new Event("change", { bubbles: true }));
  78  |   });
  79  | 
  80  |   await page.getByLabel("新 branch 名称").fill(branchName);
  81  |   await page.getByRole("button", { name: "从当前 commit point 创建 branch" }).click();
  82  |   await expect(page.getByRole("button", { name: `切换到 branch ${branchName}` })).toBeVisible();
  83  | 
  84  |   const screenshotPath = testInfo.outputPath("runtime-console.png");
  85  |   await page.screenshot({ path: screenshotPath, fullPage: true });
  86  | 
  87  |   const downloadPromise = page.waitForEvent("download");
  88  |   await page.getByRole("button", { name: "下载 evidence bundle" }).click();
  89  |   const download = await downloadPromise;
  90  |   await download.saveAs(testInfo.outputPath("evidence-bundle.json"));
  91  |   await expect(page.getByText(/已下载：evidence-bundle-/)).toBeVisible();
  92  | 
  93  |   const sessionsResponse = await request.get(`${apiBase}/sessions`);
  94  |   expect(sessionsResponse.ok()).toBeTruthy();
  95  |   const sessionsPayload = await sessionsResponse.json();
  96  |   const session = sessionsPayload.sessions.find((item: { session_name: string }) => item.session_name === sessionName);
  97  |   expect(session).toBeTruthy();
  98  | 
  99  |   const evidenceResponse = await request.get(`${apiBase}/sessions/${session.id}/evidence/bundle/manifest`);
  100 |   expect(evidenceResponse.ok()).toBeTruthy();
  101 |   const evidencePayload = await evidenceResponse.json();
  102 |   await fs.writeFile(testInfo.outputPath("evidence-bundle-manifest.json"), JSON.stringify(evidencePayload, null, 2));
  103 |   await writeHandoffArtifact(testInfo, "manifest.json", evidencePayload.manifest);
  104 | 
  105 |   await expect(page.getByText(`v0.8 scenario：${scenario}`)).toBeVisible();
  106 |   await expect(page.getByText(/结果状态：pass|结果状态：fail|结果状态：blocked|结果状态：not_run|结果状态：unknown/)).toBeVisible();
  107 |   await expect(page.getByText(/Redaction scan：pass|Redaction scan：fail|Redaction scan：not_run/)).toBeVisible();
  108 | 
  109 |   const runId = evidencePayload.manifest.latest_validation_run_id;
  110 |   expect(runId).toBeTruthy();
  111 | 
  112 |   const operationLogResponse = await request.get(`${apiBase}/validation-runs/${runId}/operation-log.jsonl`);
  113 |   expect(operationLogResponse.ok()).toBeTruthy();
  114 |   await fs.writeFile(testInfo.outputPath("agent-run.jsonl"), await operationLogResponse.text());
  115 | 
  116 |   const apiSummaryResponse = await request.get(`${apiBase}/validation-runs/${runId}/api-summary`);
  117 |   expect(apiSummaryResponse.ok()).toBeTruthy();
  118 |   await fs.writeFile(testInfo.outputPath("api-summary.json"), JSON.stringify(await apiSummaryResponse.json(), null, 2));
  119 | 
  120 |   const artifactsResponse = await request.get(`${apiBase}/sessions/${session.id}/evidence/bundle/artifacts?scenario=${scenario}`);
  121 |   expect(artifactsResponse.ok()).toBeTruthy();
  122 |   const artifacts = await artifactsResponse.json();
  123 |   for (const [name, payload] of Object.entries(artifacts)) {
  124 |     await writeHandoffArtifact(testInfo, name, payload);
  125 |   }
  126 | });
  127 | 
```