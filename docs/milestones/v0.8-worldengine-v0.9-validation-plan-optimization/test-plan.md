# Test Plan

Chinese mirror: `test-plan.zh.md`.

Run documentation checks, API tests, web tests/builds, v0.8 E2E when present,
and the WorldEngine saved-result checker when a checker-compatible result
directory is exported.

Required broad commands:

```bash
cd apps/api && uv run pytest -q
pnpm --dir apps/web test
pnpm --dir apps/web build
pnpm run test
pnpm run build
git diff --check
```
