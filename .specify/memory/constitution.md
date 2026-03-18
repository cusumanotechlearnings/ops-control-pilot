<!--
Sync Impact Report
- Version change: 1.0.0 → 2.0.0
- Modified principles: Core Web Discipline → Marketing Operations AI multi-agent rules
- Added sections: Architecture, Agent Behavior, Security, Code Quality, Testing, User Experience, Open Decisions
- Removed sections: Additional Engineering Constraints, Delivery Workflow & Quality Gates (superseded by new sections)
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check can reference agent behavior and architecture)
  - ✅ .specify/templates/spec-template.md (Remains compatible; no structural changes required)
  - ✅ .specify/templates/tasks-template.md (Phase structure aligns with testing and quality requirements)
- Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Set to the actual date this constitution is formally adopted by the team
-->

# Marketing Operations AI — Agent Constitution

*Version 2.0 — Governing principles for a multi-agent marketing operations application*

---

## ARCHITECTURE (Immutable — AI must never suggest alternatives)

These decisions are locked. No agent, developer, or AI assistant may propose substitutions or alternatives.

| Layer | Technology |
|---|---|
| Agent framework | Agno only |
| AI model | claude-opus-4-5 only |
| Database | Neon Postgres (read-only) |
| Backend | FastAPI + Python 3.11 |
| Frontend | Next.js + Tailwind CSS + TypeScript |
| Project management | Airtable via pyairtable |
| Deployment — frontend | Vercel |
| Deployment — backend | Railway |

Any suggestion to swap, supplement, or abstract any of the above is out of scope and must be rejected.

---

## AGENT BEHAVIOR

### Clarification-First Principle

The orchestrator must ask one focused clarifying question at a time before calling any specialist agent. It never
assumes intent, never batches multiple questions, and never calls a specialist agent when the user's request is
ambiguous. A clarifying question may present clickable option chips when the answer set is finite and well-defined.
When the answer is open-ended, the question must be free-text only.

### Single Responsibility

Each agent has exactly one job and must not perform work outside its defined scope. This boundary is hard and
unconditional — the orchestrator may never perform specialist work as a fallback, even when a specialist agent is
unavailable or has failed. Boundary violations are bugs, not optimizations.

### Confirmation Before Write Actions

The ops/PM agent must never create an Airtable ticket without:

1. Showing the user a full preview of all ticket fields to be created, and
2. Receiving explicit confirmation in the current thread.

A "maybe," a non-response, or an ambiguous reply is not a confirmation. The preview must be shown before confirmation
is requested — never after.

### Session Memory

Agents must use the full conversation history for the current session and must never ask the user for information
already provided in the thread. Input is always single-session (not persisted across page reloads or new browser
sessions).

### Context Window Management

When conversation history approaches the model's context limit, the system must:

1. Automatically summarize the key facts, decisions, and context from the current session into a structured handoff
   summary.
2. Start a new conversation thread, injecting the handoff summary as the opening system context.
3. Notify the user naturally (e.g., "I've started a fresh session and carried over our key context — here's what I've
   kept...").

This ensures session continuity without degrading model accuracy from an oversaturated context window. Accuracy takes
priority over unbroken thread continuity.

### Agent Attribution

Every response must display a visible label identifying which agent produced it (e.g., "Data Agent", "Ops Agent",
"Orchestrator"). Attribution is shown in the final response — not hidden, not reserved for loading states only. All
agents speak in a single consistent product voice; attribution is for transparency, not personality differentiation.

### Per-Agent Failure Rules

Each specialist agent defines its own failure behavior. Failure rules must be specified per agent at implementation
time. All failure responses must be user-facing, clear, and honest — silent failures are not permitted. The orchestrator
never absorbs or masks a specialist failure by substituting its own output.

---

## SECURITY

### Secrets Management

- `.env` is always in `.gitignore` — non-negotiable and must be enforced at repo initialization
- No API keys, tokens, or secrets in source code, comments, docstrings, or commit messages
- All environment variables loaded via `os.getenv()` with `load_dotenv()`

### Database Security

- All Neon Postgres queries that include any user input must use parameterized queries — no exceptions
- Read-only access is enforced at the tool level in code, not delegated to prompt instructions
- When a query receives input that appears to be a SQL injection attempt, the tool must block the request, return a
  user-facing explanation, and log the attempt. It must not strip and proceed.

---

## CODE QUALITY

### Python

- Type hints required on all function signatures
- Docstrings required on all `@tool` functions — these are read by Claude to decide when to call the tool, so a missing
  docstring is a functional bug, not a style issue
- PEP 8 formatting, max line length 88 characters
- No bare `except` clauses
- All environment variables via `os.getenv()` with `load_dotenv()`

### TypeScript

- Strict mode enabled
- No `any` types

### Frontend

- No inline styles — Tailwind utility classes only

---

## TESTING

### Coverage Requirements

- Every `@tool` function must have a unit test for the happy path and one for the error path
- SQL injection prevention must be explicitly tested with representative malicious input
- The Airtable ticket preview-then-confirm flow must be tested, including the case where confirmation is ambiguous or
  absent

---

## USER EXPERIENCE

### Design Philosophy

- **Restraint over decoration** — every UI element earns its place; no element is added for visual interest alone
- **Clarity over cleverness** — all copy is instantly understandable on first read
- **Consistency over novelty** — the same patterns are used throughout the interface; novel patterns require
  justification

### Interaction Behavior

- User messages appear in the thread immediately on send, before the API responds
- Input is disabled during loading
- Clarifying questions never show agent chain indicators or loading state labels
- Substantive answers always end with 1–2 natural follow-up offers, written as prose — never a bulleted options menu

### Loading States

Loading indicators must show contextual labels that reflect what is actually happening:

| State | Label |
|---|---|
| Model thinking / routing | Thinking |
| Database query in progress | Querying data |
| Processing query results | Analyzing results |
| Generating marketing output | Generating ideas |
| Preparing Airtable ticket | Creating ticket |

### Output Formatting

- Tables render as styled HTML with alternating row shading — never raw markdown
- Numbers and currency are formatted with commas and appropriate symbols (e.g., $1,234 not 1234)
- Agent attribution label is displayed on every response (see Agent Attribution above)

### Empty State

The empty state must include 3–4 clickable suggestion chips drawn from real demo questions — not generic placeholders.
These chips send the question directly into the thread on click.

---

## OPEN DECISIONS (must be resolved before first production deploy)

The following items were intentionally deferred and must be specified before the system is considered production-ready:

| Decision | Status | Notes |
|---|---|---|
| Per-agent failure rules | Pending | Must be defined for each specialist agent individually |

---

## Governance

This constitution governs all agent behavior, code standards, security posture, and UX patterns for the Marketing
Operations AI application.

- Conflicts between implementation convenience and any rule in this document are resolved in favor of this document.
- Amendments MUST be made by updating this file and clearly documenting changes in the Sync Impact Report comment at
  the top.
- Backwards-incompatible changes to principles, architecture, or governance MUST bump the MAJOR version.
- Adding new principles or materially expanding guidance MUST bump the MINOR version.
- Wording-only clarifications that do not change behavior MAY bump the PATCH version.

**Version**: 2.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Set when team formally adopts this document | **Last Amended**: 2026-03-17

<!--
Sync Impact Report
- Version change: 0.0.0 → 1.0.0
- Modified principles: [template placeholders] → Core Web Discipline
- Added sections: Additional Engineering Constraints, Delivery Workflow & Quality Gates
- Removed sections: None (template sections specialized, not removed)
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check references updated conceptually)
  - ✅ .specify/templates/spec-template.md (No constitution-driven changes required)
  - ✅ .specify/templates/tasks-template.md (Phase structure already aligned with constitution)
  - ⚠ .cursor/commands/*.md (reviewed; no agent-name issues found, but revisit if commands move under .specify/templates/commands/)
- Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Set to the actual date this constitution is formally adopted by the team
-->

# Ops Control Pilot Constitution

## Core Principles

### I. Spec-First, User-Centered Workflows

All meaningful changes MUST start from a written feature specification created through the `/speckit.specify`
and `/speckit.plan` flows.

- Every feature begins with a user-focused spec that describes scenarios, requirements, and success criteria
  without implementation details.
- Specifications MUST be clear enough that a non-technical stakeholder can understand scope and value.
- Planning artifacts (plan, research, data-model, contracts, tasks) MUST trace back to user stories in the spec.
- When trade-offs are made, the impact on users MUST be explicitly documented in the spec or plan.

**Rationale**: Ops Control Pilot exists to operationalize workflows reliably. A spec-first approach ensures we
optimize for real user outcomes instead of ad-hoc technical changes.

### II. Testable, Incremental Delivery

Features MUST be broken down into independently testable user stories and delivered incrementally.

- `/speckit.specify` MUST define user stories that can be implemented, tested, and validated independently.
- `/speckit.tasks` MUST organize tasks by user story so each story can be delivered as a standalone increment.
- No user story is "done" until it has clear acceptance criteria and can be validated in isolation.
- MVP delivery (P1 stories) is prioritized over broad, partially-complete functionality.

**Rationale**: Incremental, testable slices reduce risk and make it easier to reason about ops impact and rollout.

### III. Enforcement via Gates (NON-NEGOTIABLE)

Constitution compliance is enforced through explicit gates in planning and tasks.

- The "Constitution Check" section in the implementation plan MUST be populated for every feature.
- Gate failures (e.g., missing spec, unclear requirements, untestable stories) MUST block planning from
proceeding until resolved.
- Foundational work (Phase 2 in `tasks-template.md`) MUST be completed before user story work begins.
- Violations of this constitution MAY be accepted only when explicitly justified in the "Complexity Tracking"
or equivalent rationale sections.

**Rationale**: Gates make the constitution operational, not aspirational, and ensure discipline even under time
pressure.

### IV. Clarity over Tooling

Templates, commands, and automation MUST clarify thinking, not obscure it.

- AI/agent commands (e.g., `/speckit.*`) MUST produce artifacts that a human can read and validate without
additional context.
- Placeholders such as `[NEEDS CLARIFICATION]` MUST be resolved or explicitly justified before implementation
starts.
- When the automation makes assumptions, these MUST be documented in the relevant artifact (spec, plan,
research, or tasks).
- Ambiguous language ("maybe", "sort of", "should probably") MUST be rewritten into concrete, testable
statements or turned into explicit clarifying questions.

**Rationale**: Ops work fails when intent is unclear. Tools exist to sharpen intent, not to hide it.

### V. Operational Readiness & Simplicity

Every change MUST be safe to operate and as simple as reasonably possible.

- Plans and tasks MUST account for observability, error handling, and rollback/mitigation where relevant.
- Quickstart and research documents MUST explain how to run, validate, and troubleshoot the feature locally.
- Additional complexity (extra services, layers, abstractions) MUST be justified in writing, including rejected
alternatives.
- Prefer small, composable building blocks over large, tightly coupled changes.

**Rationale**: Ops Control Pilot is an operational tool; operability and simplicity directly impact reliability.

## Additional Engineering Constraints

For this repository:

- Primary stack: Next.js (React) with TypeScript.
- All UI work MUST follow accessibility best practices (semantic HTML, keyboard navigation, ARIA where needed).
- Performance and bundle size MUST be considered for every major UI feature; lazy loading SHOULD be used for
heavy, non-critical paths.
- Security-sensitive changes (authentication, authorization, secrets, integrations) MUST include explicit notes
in the spec and plan about risks and mitigations.

Cross-cutting constraints:

- Artifacts generated by `/speckit.*` commands MUST remain in sync with this constitution.
- Any manual deviation from templates MUST be documented in the relevant artifact.
- Repository automation (scripts, agents) MUST be treated as production code (versioned, reviewed, and tested
when possible).

## Delivery Workflow & Quality Gates

The end-to-end feature delivery workflow is:

1. **Specify**: Use `/speckit.specify` to create or update `spec.md` for the feature.
2. **Plan**: Use `/speckit.plan` to generate `plan.md`, `research.md`, `data-model.md`, `contracts/` (if
   applicable), and `quickstart.md`.
3. **Tasks**: Use `/speckit.tasks` to generate `tasks.md` grouped by user story and phases.
4. **Implement**: Implement tasks in priority order (MVP first), keeping artifacts in sync as scope evolves.
5. **Review**: Code review MUST check compliance with this constitution and confirm gates have been honored.

Quality gates:

- No feature MAY enter planning without a valid spec.
- No implementation MAY start while "Foundational (Phase 2)" tasks are incomplete, unless explicitly carved out
  and justified.
- No feature MAY be considered complete until:
  - User stories marked as done are independently testable.
  - Success criteria from the spec are evaluated.
  - Quickstart is accurate and up to date.

## Governance
The Ops Control Pilot Constitution governs how features are specified, planned, implemented, and reviewed.

- This constitution supersedes conflicting local practices for work executed via `/speckit.*` commands.
- Amendments MUST be made by updating this file and clearly documenting changes in the Sync Impact Report
  comment at the top.
- Backwards-incompatible changes to principles or governance MUST bump the MAJOR version.
- Adding new principles or materially expanding guidance MUST bump the MINOR version.
- Wording-only clarifications that do not change behavior MAY bump the PATCH version.
- All pull requests that modify specs, plans, tasks, or automation MUST confirm continued compliance with this
  constitution.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Set when team formally adopts this document | **Last Amended**: 2026-03-17
