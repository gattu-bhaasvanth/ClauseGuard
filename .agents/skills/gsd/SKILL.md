---
name: gsd
description: "Spec-Driven Development (SDD) meta-prompting and execution framework for software delivery: milestone planning, phase execution, verification gates, autonomous workflows, and atomic shipping."
argument-hint: "<command> [args...]"
---

# GSD (Get Shit Done) — Spec-Driven Development System

## Overview

**GSD (Get Shit Done)** turns complex, multi-phase engineering objectives into reliable, shipped software through an explicit, resumable workflow:
`explore → plan → execute → verify → ship`.

Work is organized into milestones and phases under a project's `.planning/` directory, with each phase carrying a `SPEC.md`, a `PLAN.md`, and strict verification criteria. The system favors small, atomic, test-backed commits and keeps durable context in version-tracked files rather than in ephemeral chat conversation.

## The Iron Laws of GSD

1. **NO EXECUTION WITHOUT A PLAN**: Never write feature code without an active phase `PLAN.md` with explicit tasks, verification criteria, and file targets.
2. **ATOMICTY & VERIFICATION**: Each task must be independently verifiable (automated test, build verification, or concrete observable evidence) before moving to the next task.
3. **DURABLE PLANNING STATE**: All project state, decisions, roadmaps, and progress are stored under `.planning/` (`ROADMAP.md`, `STATE.md`, `PHASE-*.md`).
4. **NO SYMPTOM FIXES**: When encountering an issue during execution, invoke systematic root-cause tracing before attempting any patch.
5. **ZERO DESTRUCTIVE SURPRISES**: Never delete databases, build artifacts, environments, or user code without explicit verification.

## Core Commands

| Command | Category | Description | Reference |
|---|---|---|---|
| `new-project` | Initialize | Initialize project roadmap, capture requirements, tech stack, and goals in `.planning/` | `references/plan-phase.md` |
| `plan-phase <N>` | Planning | Break milestone phase `<N>` into atomic, test-backed tasks with verification gates in `PLAN.md` | `references/plan-phase.md` |
| `execute-phase <N>` | Execution | Execute all tasks in phase `<N>` with wave-based or sequential dependency handling and TDD | `references/execute-phase.md` |
| `quick <task>` | Rapid | Execute a small, self-contained task (1-2 files) with TDD and immediate verification | `references/quick.md` |
| `verify-work <N>` | Quality | Verify phase implementation against spec criteria, automated test suites, and regression checks | `references/verify-work.md` |
| `ship <N>` | Delivery | Finalize phase `<N>`, update roadmap, generate changelog/release notes, and archive artifacts | `references/ship.md` |
| `progress` / `health` | Status | Inspect current milestone progress, blockers, completed phases, and remaining scope | `references/plan-phase.md` |
| `pause-work` / `resume-work` | Session | Serialize active context to `.planning/STATE.md` or restore context after a session break | `references/execute-phase.md` |
| `debug <issue>` | Diagnosis | Enter systematic diagnosis loop: observe symptom → trace root cause → minimal fix → verify | `systematic-debugging` |

## Detailed Workflow Instructions

### 1. Planning a Phase (`plan-phase <N>`)
- Read project context, requirements, and existing architecture.
- Identify the exact scope boundaries for Phase `<N>`.
- Generate `.planning/phase-<N>/PLAN.md` defining:
  - Objective and acceptance criteria.
  - Wave breakdown (Wave 1: core/models, Wave 2: business logic/endpoints, Wave 3: UI/integration).
  - Explicit test cases and automated verification commands.
- See `references/plan-phase.md` for full parameter flags (`--tdd`, `--mvp`, `--skip-research`, etc.).

### 2. Executing a Phase (`execute-phase <N>`)
- Load `.planning/phase-<N>/PLAN.md`.
- For each task in the plan:
  1. Write failing test or verification criteria first (TDD).
  2. Implement minimal code to satisfy the requirement.
  3. Run test suite to verify success and ensure zero regressions.
  4. Record checkpoint in `.planning/phase-<N>/STATE.md`.
- See `references/execute-phase.md` for wave filtering and gap closure workflows.

### 3. Rapid Execution (`quick <task>`)
- For focused bug fixes, isolated components, or minor refactors that don't need a full milestone phase.
- Clarify goal, implement with automated tests, verify pass, and commit.
- See `references/quick.md`.

### 4. Verification & Gap Closure (`verify-work <N>`)
- Audit deliverables against the phase `SPEC.md` or roadmap acceptance criteria.
- Run full automated test suites (backend unit/integration tests, frontend tests, linting, build checks).
- If gaps or failures exist, generate gap closure plans (`--gaps-only`) and execute them before marking phase complete.
- See `references/verify-work.md`.

### 5. Shipping & Milestone Completion (`ship <N>`)
- Confirm all verification gates pass.
- Update `ROADMAP.md` marking Phase `<N>` as completed.
- Create milestone summary and release notes.
- See `references/ship.md`.
