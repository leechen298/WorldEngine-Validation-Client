# Natural Language Routing

Chinese mirror: `routing.zh.md`.

Natural-language requests route work to milestone, spec, or ADR documents.
Routing never authorizes skipping documentation, verification, review records,
or task-level commits.

| User request | Route | Required documents |
| --- | --- | --- |
| develop v0.1, implement v0.1, continue v0.1, `/goal develop v0.1` | `docs/milestones/v0.1-foundation/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| plan v0.2, create v0.2 docs, prepare v0.2 | create or update `docs/milestones/v0.2-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| develop vX.Y, implement vX.Y, continue vX.Y, `/goal develop vX.Y` | matching `docs/milestones/vX.Y-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md` |
| review vX.Y, inspect vX.Y, audit vX.Y | matching `docs/milestones/vX.Y-*/` | `README.zh.md`, `plan.zh.md`, `review.zh.md`, current git diff |
| change tech stack, explain a technology choice, architecture decision | `docs/adr/` | relevant ADR, or create a new ADR before changing architecture |
| update overall design, change product boundary, revise validation-client design | `docs/specs/validation-client-design.zh.md` | design spec plus affected milestone docs |

For versions not listed above, route to the matching directory under
`docs/milestones/`.

If the directory or plan does not exist, stop and create or request milestone
documentation before implementation.

## Milestone Documentation Standard

Every milestone must have detailed documents before implementation starts:

- `README.zh.md`: status, goal, scope, non-goals, and entry rules.
- `plan.zh.md`: numbered tasks, files, verification commands, and expected
  commit boundaries.
- `review.zh.md`: task records, command results, scope review, and final
  assessment.

Before implementation, `review.zh.md` may record that implementation is
pending. It must not claim implemented, complete, or equivalent status until
the completion gate in `workflow.md` is satisfied.

If implementation reveals that `plan.zh.md` is wrong or incomplete, stop,
update milestone documents, and resume only after the updated scope is clear.
Do not silently improvise around the plan.
