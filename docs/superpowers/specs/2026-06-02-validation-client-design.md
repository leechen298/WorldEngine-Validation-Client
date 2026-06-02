# WorldEngine Validation Client Design

Status: draft for user review
Date: 2026-06-02

## Objective

`WorldEngine-Validation-Client` is a standalone web-first validation client for
observing, replaying, and branching WorldEngine runtime sessions.

The first version should make a generated WorldEngine world visible to humans,
support high-level director guidance, preserve replayable local evidence, and
stay compatible with a future game-client direction.

This repository is independent from the WorldEngine core repository.

## Product Position

The client is not a thin engineering dashboard and not a full game client. It
is an observation-first, director-assisted validation experience:

- The user observes a world that WorldEngine creates and evolves.
- The user can guide the broad direction of world evolution.
- The user does not enter the world as a player character.
- The user does not place items, directly trigger concrete events, or edit
  agent internals.
- The client visualizes and records what WorldEngine exposes through public
  APIs.

The future production game client may use a different runtime or presentation
stack. This validation client should still use a storage and session model that
can evolve toward game-style saves, replay, and timeline branching.

## Repository Boundary

WorldEngine and `WorldEngine-Validation-Client` are separate repositories.

The validation client must not:

- import WorldEngine source code.
- depend on private WorldEngine local paths.
- call WorldEngine internal helpers.
- manage LLM API keys.
- call LLM providers directly.
- generate authoritative world facts.
- mutate agent memory, goals, identity, self-state, or decisions directly.

The validation client may communicate with WorldEngine only through public
interfaces:

- `WORLDENGINE_API_BASE`.
- public HTTP APIs.
- public schemas, manifests, and OpenAPI descriptions.
- public event, state, timeline, and evaluator outputs.

## Responsibility Split

### WorldEngine

WorldEngine owns all core runtime behavior:

- LLM provider and API key handling through environment configuration.
- world generation from a natural-language world premise.
- generated scene, item, actor, rule, and initial-state material.
- autonomous world evolution.
- random event generation.
- agent cognition, pseudo-self behavior, memory use, goals, and actions.
- evaluator logic and public evaluator outputs.
- authoritative runtime state.

### Validation Client Backend

The local validation backend is part of this repository. It stores and serves
client-side session data, but it does not become a WorldEngine subsystem.

It owns:

- session creation and local metadata.
- timeline and branch records.
- event and diff persistence.
- periodic snapshots.
- replay and fork APIs for the web frontend.
- redacted API trace records.
- local evidence bundle export.
- optional proxying to WorldEngine public APIs.

It does not generate world content or authoritative facts.

### Web Frontend

The frontend owns the human experience:

- session library.
- world creation entry.
- pixel-world observation surface.
- runtime controls.
- high-level director input.
- timeline scrubber.
- replay and fork UI.
- agent public-state panel.
- event and life-log panels.
- local evidence bundle export.

## Technical Stack

First-version stack:

- frontend: React, Vite, TypeScript.
- pixel scene: PixiJS.
- frontend state: Zustand.
- backend: Python, FastAPI, Pydantic.
- database: SQLite.
- packaging for development: web frontend plus local FastAPI backend.

SQLite is the first-version database because it supports durable local storage,
append-only logs, snapshots, timeline branching, and export without requiring a
server database. Postgres can be considered later for cloud or multi-user
deployment.

## Main Screens

### Session Library

The first screen is a session and world-line library.

It should show:

- WorldEngine connection status.
- WorldEngine API base URL.
- health, version, and public capability manifest summary.
- create-new-world entry.
- saved sessions.
- latest tick, latest event summary, and last-run timestamp.
- timeline branch count.
- import, export, archive, and cleanup actions.

The user selected this as the first-screen model during design review because
it feels closer to a game save/world list than a one-off test console.

### Runtime Console

Opening a session enters the runtime console.

It should include:

- left-side controls for run, pause, continue, single tick, director guidance,
  and branch selection.
- central pixel-world view driven by public WorldEngine state.
- timeline scrubber with tick, snapshot, event markers, replay jump, and
  fork-from-here controls.
- right-side panels for agent public state, event/life logs, diffs, warnings,
  errors, and evidence export.

## Core Flows

### Create World

The user enters a natural-language world premise.

WorldEngine turns the premise into structured world content and returns public
initial state and visualization payloads. The client stores the premise,
request metadata, returned public state, and initial snapshot.

### Run World

WorldEngine advances the world by time or tick.

The client records:

- public event envelopes.
- visual state diffs.
- periodic snapshots.
- API traces.
- warnings and errors.

WorldEngine owns the actual time progression, state transitions, agent action,
memory use, random event generation, and evaluator behavior.

### Director Guidance

The user can enter high-level natural-language direction during runtime.

Director guidance:

- affects only external world environment and event tendencies.
- enters a queue or pending state.
- is inserted by WorldEngine at an appropriate evolution point.
- is logged with raw text, accepted timing, structured public interpretation,
  and resulting public effects when available.

Director guidance must not:

- directly alter agent internal thoughts.
- directly alter memory records.
- directly set goals.
- force agent actions.
- force relationship or identity changes.
- overwrite world facts in a hidden way.

Agents must react from their own state, memory, goals, history, relationships,
and perceived public events.

### Replay

The user can move back to a prior tick or event point.

Replay is reconstructed by:

1. finding the nearest earlier snapshot.
2. applying forward diffs until the selected tick.
3. rendering the reconstructed public visual state.

Replay is a client-side visualization and evidence feature. It does not rewrite
WorldEngine authoritative runtime state.

### Fork Timeline

The user can branch from a historical tick.

A fork is similar to a code branch. It records where the new branch came from,
but it does not create a parent-child hierarchy between timelines.

A fork records:

- source timeline or branch id.
- fork base tick.
- fork base snapshot reference.
- optional fork reason or director guidance.
- new timeline id.

The new timeline then continues as an independent peer branch. It does not
overwrite or become subordinate to the source timeline.

### Export Evidence Bundle

The client can export a local session evidence bundle.

The bundle is not a heavy evaluator report. It is evidence for Codex, humans,
or later WorldEngine review:

- session metadata.
- WorldEngine version and capability summary.
- director inputs.
- event log.
- state diffs.
- snapshots.
- replay index.
- redacted API traces.
- public evaluator outputs from WorldEngine, if available.
- warnings and errors.

## Storage Model

The storage model is event-sourced with periodic snapshots.

Primary tables:

- `sessions`
- `timelines`
- `events`
- `state_diffs`
- `snapshots`
- `director_intents`
- `api_traces`
- `worldengine_runs`
- `replay_index`

Storage rules:

- Store public event envelopes as audit records.
- Store state changes as forward diffs.
- Store complete snapshots every N ticks or at key events.
- Reconstruct historical visual state from snapshot plus forward diffs.
- Use timeline branches instead of overwriting history.
- Prefer readable JSON in the first version.
- Add gzip or zstd compression for large snapshots or exported bundles after
  the basic model is working.

The client-side database is not the authoritative WorldEngine state. It is the
local observation, replay, fork, and export store.

## Logging

The client should store complete local logs for its own session.

Log categories:

- session lifecycle.
- world events.
- visual state diffs.
- agent public life events.
- director guidance.
- timeline and fork actions.
- API trace summaries.
- warnings and errors.
- WorldEngine evaluator outputs, when public.

Logs must be redacted. They must not include LLM API keys, provider secrets,
private prompts, private oracle internals, or non-public WorldEngine internals.

## API Shape

The backend should expose local client APIs for:

- connection status.
- session CRUD.
- world creation request.
- run, pause, continue, and tick commands.
- director guidance submission.
- timeline list and selection.
- replay reconstruction.
- fork creation.
- log querying.
- evidence bundle export.

WorldEngine API details remain external and should be discovered from its
public API, manifest, or OpenAPI surface.

## Non-Goals For First Version

The first version should not implement:

- player-character control.
- direct item placement.
- direct manual event injection.
- direct editing of agent memory, goals, identity, relationships, or actions.
- custom LLM provider calls in the client.
- LLM API key management in the client.
- heavy evaluator logic in the client.
- private WorldEngine integration.
- cloud sync.
- multiplayer.
- production game packaging.

## Open Implementation Details

These should be decided during implementation planning:

- exact WorldEngine public API endpoints.
- visualization payload schema.
- diff format, likely JSON Patch inspired.
- snapshot cadence.
- SQLite schema details and indexes.
- evidence bundle file layout.
- frontend component breakdown.
- development scripts and process manager.
- test strategy for replay and fork correctness.
