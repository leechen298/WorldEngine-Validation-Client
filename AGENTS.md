# AGENTS.md

This repository is an external WorldEngine client and independent validator.
The active goal is documented in `docs/current/MVP.zh.md`.

Historical milestone files under `docs/milestones/` are reference material.
They do not require a new milestone package, task-by-task commits, or review
records before implementation.

## Hard Boundaries

1. Communicate with WorldEngine through public HTTP, OpenAPI, manifests, and
   public evidence only. Never import WorldEngine source or read its storage.
2. The Godot executor renders public projections and records raw execution
   evidence. It must not write PASS/FAIL verdicts.
3. The checker is a separate process, must not import executor code, and alone
   owns the final verdict.
4. This repository does not own LLM keys, authoritative world facts, private
   Agent state, or provider traces.
5. Preserve legacy Web/API code unless the active MVP requires a scoped
   compatibility fix. Do not use legacy green E2E results as MVP PASS.
6. Verify claims with commands run in the current work session.
7. Preserve unrelated user changes and avoid destructive git operations.

Implement complete vertical slices directly. Keep current decisions and
evidence in `docs/current/MVP.zh.md`; detailed milestone documents and routine
evaluator gates are optional.
