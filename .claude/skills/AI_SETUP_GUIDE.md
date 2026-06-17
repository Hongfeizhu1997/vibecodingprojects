# Studio - AI Setup Guide

> This file is written for an AI assistant to read and execute.
> Goal: generate a complete Studio workspace folder structure for the user.

## What You Are Building

Studio is a structured local workspace for AI-assisted product, project, and tool development.

The design goal is simple:

- any new AI session should have one clear entry point
- durable context should be separated from temporary work
- project truth should live inside each project folder
- the user should not need to re-explain stable preferences every time

In the current Studio model, `Agent.md` is the single top-level entry point for all AI tools, not just Claude.

## Instructions

1. Ask the user for their preferred root path.
2. Ask the user the onboarding questions below.
3. Create the folder structure and files in this guide.
4. Customize the files with the user's answers.
5. Do not leave placeholder text in final files unless the user explicitly wants a draft.

## Onboarding Questions

Before generating files, ask:

1. Who are you?
   Role, background, current direction, and the kinds of projects you usually work on.
2. How do you like to work with AI?
   Concise or detailed, ask-first or execute-first, what to avoid.
3. What is your first project?
   Project name plus one-sentence description.
4. Is the project `enterprise` or `personal`?
   Do not skip this classification.
5. What AI tools do you use?
   For example: Claude, Codex, Cursor, ChatGPT, VS Code.

## Folder Structure To Create

```text
Studio/
├── Agent.md
├── 01_CONTEXT/
│   ├── README.md
│   ├── IDENTITY/
│   │   └── WHO_I_AM.md
│   ├── WORKSTYLE/
│   │   ├── HOW_I_WORK.md
│   │   └── AI_TASK_TRIAGE.md
│   ├── STANDARDS/
│   │   ├── AI_WORKFLOW.md
│   │   ├── CODING_STYLE.md
│   │   ├── FILE_STRUCTURE.md
│   │   └── TESTING.md
│   └── DOMAIN/
├── 02_PROJECTS/
│   └── [first_project_name]/
│       ├── README.md
│       ├── PRODUCT_REQUIREMENTS.md
│       ├── DECISIONS.md
│       ├── SESSION_HANDOFF.md
│       ├── tests/
│       │   ├── README.md
│       │   └── fixtures.json
│       └── archive/
│           └── reports/
├── 03_WORK/
│   ├── current_focus.md
│   ├── inbox/
│   │   └── README.md
│   └── incubator/
│       └── .gitkeep
├── 04_RESOURCES/
│   ├── TEMPLATES/
│   │   ├── DECISIONS_TEMPLATE.md
│   │   ├── SESSION_HANDOFF_TEMPLATE.md
│   │   └── PRODUCT_REQUIREMENTS_TEMPLATE.md
│   └── tools/
│       └── .gitkeep
```

## File Templates

### Agent.md

```markdown
# Studio Master Entry

This file is the primary AI entry point for [USER_STUDIO_PATH].

Despite the filename, it is not Claude-only. Any AI working inside this workspace should treat this file as the top-level operating contract.

Studio is a structured workspace for AI-assisted product, project, and tool development.

## Mandatory Start Rule

For any meaningful task in this workspace, read files in this order:

1. `Agent.md`
2. `01_CONTEXT/IDENTITY/WHO_I_AM.md`
3. `01_CONTEXT/WORKSTYLE/HOW_I_WORK.md`
4. `03_WORK/current_focus.md`
5. target project `README.md`
6. target project `SESSION_HANDOFF.md` if active work exists
7. additional files from `STANDARDS/` or `DOMAIN/` only when relevant

Do not skip steps 2 to 4.

## Core Behavior Rules For AI

- Read context before acting.
- If requirements are unclear, conflicting, or structurally significant, stop and ask.
- If the scope is clear, execute directly.
- If an action is risky or irreversible, warn before proceeding.
- Keep durable context in `01_CONTEXT/`.
- Keep project truth in the relevant project folder.
- Keep temporary notes and intermediate materials out of `01_CONTEXT/`.

## Project Admission Rule

- Put work in `02_PROJECTS/` when it has a distinct deliverable and will likely need repeated sessions.
- Put work in `03_WORK/` when it is active but still temporary or coordination-heavy.
- Put work in `03_WORK/incubator/` when it is disposable and not yet trusted.

Any item promoted into `02_PROJECTS/` should aim to have:

- `README.md`
- `SESSION_HANDOFF.md`
- `DECISIONS.md`
- `PRODUCT_REQUIREMENTS.md` once scope becomes concrete
```

### 01_CONTEXT/README.md

```markdown
# Studio Context

This folder stores durable context for AI-assisted work.

Core read order after `Agent.md`:

- `IDENTITY/WHO_I_AM.md`
- `WORKSTYLE/HOW_I_WORK.md`
- then task-relevant files from `STANDARDS/` or `DOMAIN/`

Structure:

- `IDENTITY`
  - who the user is
- `WORKSTYLE`
  - how the user prefers to work and make decisions
- `STANDARDS`
  - cross-project workflow, coding, testing, and file-structure rules
- `DOMAIN`
  - durable business or subject-matter knowledge
```

### 01_CONTEXT/IDENTITY/WHO_I_AM.md

```markdown
# Who I Am

Status: Stable context
Last updated: [DATE]

## Role Summary

- [who the user is]
- [their role in this workspace]
- [how AI should treat them as a collaborator]

## Background

- [professional background]
- [typical areas of experience]
- [types of projects they usually work on]

## Typical Project Shape

- [common project types]
- [common business or technical patterns]

## Current Direction

- [what the user is building or learning now]
- [what long-term capability they want to build]

## Stable Collaboration Preferences

- [stable communication preference]
- [stable expectation from AI]

## Implementation Preferences

- [project structure preference]
- [documentation preference]
- [naming and complexity preference]
- [trade-off order]

## Long-Term Goals

- [goal 1]
- [goal 2]

## Non-Goals

- [what should not be optimized too early]
- [what should be avoided]
```

### 01_CONTEXT/WORKSTYLE/HOW_I_WORK.md

```markdown
# How I Work

Status: Active
Last updated: [DATE]

## Tools & Roles

| Tool | Purpose |
|---|---|
| [tool] | [purpose] |

## Preferred Way of Working

- Discuss first, then implement.
- Produce a concrete plan before writing substantial code.
- Aim for reusable workflows across sessions.

## New Task Startup Rule

1. Read `Agent.md`
2. Read `WHO_I_AM.md`
3. Read this file
4. Read `03_WORK/current_focus.md`
5. Read the target project's `README.md` and `SESSION_HANDOFF.md` if the task is project-specific
6. Read `AI_TASK_TRIAGE.md` when the task has mixed inputs, multiple possible framings, or high review cost

## What I Want From AI

- Practical, reliable recommendations
- Clear tradeoff explanations
- Help turning ideas into structured documents before coding
- Immediate flagging of conflicts or ambiguities

## When AI Should Stop And Ask

- When requirements are ambiguous or conflicting
- When a change touches file structure or project organization
- When the right approach requires a trade-off not yet addressed

## Decision Style

- Prefer minimal-disruption changes when the existing direction is workable
- Prefer practical progress over theoretical completeness
- Prefer structured plans before migrations, reorganizations, or multi-step changes

## Risk Handling

Be conservative when the task involves:

- file moves or deletions
- data modification
- release actions
- irreversible cleanup

Be more aggressive when:

- requirements are already clear
- implementation is local and reversible
- a better structure can be proposed with clear reasoning

## What To Avoid

- Messy or inconsistent style
- Changing things outside the current scope
- Long explanations when a short answer would do
```

### 01_CONTEXT/WORKSTYLE/AI_TASK_TRIAGE.md

```markdown
# AI Task Triage

Status: Active
Last updated: [DATE]

## Why This Exists

For messy real-world inputs, the common failure mode is choosing the wrong problem shape too early.

Preferred pattern:

- classify the task first
- partition the data if needed
- identify the easiest high-confidence slice
- validate the slice-specific approach
- only then scale implementation

## Default Triage Sequence

1. Inventory
2. Segmentation
3. Success Slice
4. Verification Plan
5. Implementation

## Rule For Future Sessions

If the task involves heterogeneous inputs, uncertain classes, or high review cost:

- propose a triage or manifest phase first
- confirm whether the user wants staged handling
- do not default to a single all-cases implementation
```

### 01_CONTEXT/STANDARDS/AI_WORKFLOW.md

```markdown
# AI Workflow

Status: Active
Last updated: [DATE]

## Goal

Define a repeatable workflow for working with AI inside Studio.

## Standard Session Start

1. Read `Agent.md`
2. Identify the target outcome
3. Read `01_CONTEXT/IDENTITY/WHO_I_AM.md`
4. Read `01_CONTEXT/WORKSTYLE/HOW_I_WORK.md`
5. Read `03_WORK/current_focus.md`
6. Read the target project's `README.md`
7. Read the project's `SESSION_HANDOFF.md` if it exists
8. Read additional standards only when the task needs them
9. Summarize assumptions before major changes

## Document Placement Rules

- `01_CONTEXT` -> durable preferences, standards, domain knowledge
- `02_PROJECTS/<project>` -> project-specific requirements, decisions, handoff, deliverables
- `03_WORK` -> current priorities, meeting notes, temporary coordination materials
- `03_WORK/incubator` -> disposable exploration
- `04_RESOURCES` -> reusable prompts, templates, patterns, and shared automation under `tools/`

## AI Rules

- discuss requirements before large implementation
- record non-obvious decisions in writing
- do not store temporary state in durable context files
- do not treat one-off notes as standards
- use `Agent.md` as the stable workspace entry point for all AI tools
```

### 01_CONTEXT/STANDARDS/FILE_STRUCTURE.md

```markdown
# File Structure

Status: Active
Last updated: [DATE]

## Rules

- `01_CONTEXT`: durable personal and AI working context
- `02_PROJECTS`: active project folders with their own local documentation
- `03_WORK`: current work materials, notes, active coordination docs
- `03_WORK/incubator`: temporary tests and explorations
- `04_RESOURCES`: reusable templates, references, prompts, and shared scripts/automation under `tools/`

## Entry Criteria

- create a folder in `02_PROJECTS` when the work has a distinct outcome or deliverable
- create content in `03_WORK` for current execution materials not durable enough for standards
- create content in `03_WORK/incubator` for disposable work not yet trusted
- promote to `04_RESOURCES` only after proving reusable across sessions or projects
- promote shared scripts into `04_RESOURCES/tools` when they become reusable infrastructure

## Project Document Standard

Each active project should have:

- `README.md`
- `PRODUCT_REQUIREMENTS.md` or equivalent
- `DECISIONS.md`
- `SESSION_HANDOFF.md`
```

### 02_PROJECTS/[project]/README.md

```markdown
# [Project Name]

[One paragraph: what this project is and why it exists]

## Status

Current phase: [phase name]
Last updated: [DATE]

## Quick Links

- [PRODUCT_REQUIREMENTS.md](./PRODUCT_REQUIREMENTS.md)
- [DECISIONS.md](./DECISIONS.md)
- [SESSION_HANDOFF.md](./SESSION_HANDOFF.md)

## For AI

Read files in this order:

1. This README
2. SESSION_HANDOFF.md
3. DECISIONS.md
4. PRODUCT_REQUIREMENTS.md if doing requirements work
```

### 02_PROJECTS/[project]/PRODUCT_REQUIREMENTS.md

```markdown
# [Project Name] Product Requirements

## Goal

What this product should achieve.

## Problem

What problem exists today and why it matters.

## Users

- Primary:
- Secondary:

## Scope

### In Scope

- [item]

### Out Of Scope

- [item]

## Functional Requirements

- [requirement]

## Non-Functional Requirements

- [requirement]

## Open Decisions

- [decision]
```

### 02_PROJECTS/[project]/DECISIONS.md

```markdown
# [Project Name] - Decisions

## Decision Log

### [DATE] - [Decision Title]

- Status: confirmed / open / superseded
- Context: [why this decision was needed]
- Decision: [what was decided]
- Consequence: [what this means]
```

### 02_PROJECTS/[project]/SESSION_HANDOFF.md

```markdown
# [Project Name] - Session Handoff

Last updated: [DATE]
Last session: [brief description]

## Current State

- project:
- status:
- blockers:

## What Changed

- [change]

## Open Items

- [ ] [item]

## Next Session Should Start With

1. [action]
```

### 03_WORK/current_focus.md

```markdown
# Current Focus

Status: Active
Last updated: [DATE]

## Current Projects

1. [PROJECT NAME]
   - Stage: [early definition / in progress / shipped]
   - Current need: [what needs to happen next]

## Immediate Priorities

- [top priority]
- [second priority]

## Open Questions

- [question]

## Notes For Next Session

- [what AI should know at the next start]
```

### 03_WORK/inbox/README.md

```markdown
# Inbox

Raw materials land here - meeting transcripts, voice memos, rough notes.

## Pipeline

1. Drop raw files here
2. Ask AI to parse and extract structured requirements, decisions, and TODOs
3. AI outputs go to the relevant project folder
4. Move processed files to `inbox/processed/`
```

### 04_RESOURCES/TEMPLATES/SESSION_HANDOFF_TEMPLATE.md

```markdown
# [Project] - Session Handoff

Last updated: [DATE]
Last session: [description]

## Current State

- project:
- status:
- blockers:

## What Changed

- [change]

## Open Items

- [ ] [item]

## Next Session Should Start With

1. [action]
```

### 04_RESOURCES/TEMPLATES/DECISIONS_TEMPLATE.md

```markdown
# [Project] - Decisions

## Decision Log

### [DATE] - [Title]

- Status: confirmed / open
- Context: [why needed]
- Decision: [what was decided]
- Consequence: [impact]
```

### 04_RESOURCES/TEMPLATES/PRODUCT_REQUIREMENTS_TEMPLATE.md

```markdown
# [Project Name] Product Requirements

## Goal

What this product should achieve.

## Problem

What problem exists today and why it matters.

## Users

- Primary:
- Secondary:

## Scope

### In Scope

- [item]

### Out Of Scope

- [item]

## Functional Requirements

- [requirement]

## Non-Functional Requirements

- [requirement]

## Open Decisions

- [decision]
```
