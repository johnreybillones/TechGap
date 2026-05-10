# TechGap — Curriculum Gap Analyzer

## Project Overview

TechGap is an ML-powered curriculum gap analysis system that compares BSCS/BSIT syllabi against Philippine job market data to produce actionable curriculum revision recommendations. It uses SBERT + Node2Vec embeddings, K-Means clustering, LambdaMART ranking, and CHED compliance guardrails.

**Tech Stack:** Next.js (TypeScript, Tailwind) · FastAPI (Python) · Supabase (PostgreSQL + pgvector) · SBERT · XGBRanker

---

## Agentic Skill Framework

This project uses three complementary skill frameworks installed globally:

| Framework          | Location                         | Purpose                                                                |
| ------------------ | -------------------------------- | ---------------------------------------------------------------------- |
| **Superpowers**    | `~/.claude/skills/superpowers/`  | Workflow methodology — planning, TDD, reviews, debugging               |
| **ECC**            | `~/.claude/skills/ecc/`          | Domain knowledge — coding standards, API design, security, DB patterns |
| **Context7**       | `~/.claude/skills/context7-mcp/` | Live documentation lookup via MCP for libraries and frameworks         |
| **Project Skills** | `.agents/skills/`                | Project-specific skills (e.g., Supabase Postgres best practices)       |

### Superpowers Bootstrap

**REQUIRED:** The `superpowers:using-superpowers` skill MUST be invoked at the start of every session. It establishes the skill discovery and invocation protocol.

**Rule:** If there is even a 1% chance a skill applies to the current task, invoke it BEFORE taking any action — including asking clarifying questions.

---

## Workflow Chains

### Building Features (New Work)

Follow this mandatory chain. Do NOT skip steps or jump to implementation.

```
1. Brainstorm  →  2. Plan  →  3. Execute  →  4. Review  →  5. Finish
```

| Step              | Skill                                                                                    | What Happens                                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Brainstorm** | `superpowers:brainstorming`                                                              | Explore intent, ask clarifying questions one at a time, propose 2-3 approaches, present design, write spec to `docs/superpowers/specs/` |
| **2. Plan**       | `superpowers:writing-plans`                                                              | Create bite-sized implementation plan with TDD steps, exact file paths, and code blocks. Save to `docs/superpowers/plans/`              |
| **3. Execute**    | `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` | Dispatch fresh subagent per task + two-stage review (spec compliance → code quality)                                                    |
| **4. Review**     | `superpowers:requesting-code-review`                                                     | Dispatch code reviewer subagent with git SHAs and plan context                                                                          |
| **5. Finish**     | `superpowers:finishing-a-development-branch`                                             | Verify tests → detect environment → present merge/PR/keep/discard options                                                               |

### Debugging (Fixing Issues)

```
1. Investigate  →  2. Hypothesize  →  3. Fix (TDD)  →  4. Verify
```

| Step               | Skill                                        | What Happens                                                                                          |
| ------------------ | -------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **1. Investigate** | `superpowers:systematic-debugging`           | Read errors carefully, reproduce, check recent changes, trace data flow. NO fixes without root cause. |
| **2. Hypothesize** | (same skill, Phase 3)                        | Form single hypothesis, test minimally, one variable at a time                                        |
| **3. Fix**         | `superpowers:test-driven-development`        | Write failing test → implement fix → verify green                                                     |
| **4. Verify**      | `superpowers:verification-before-completion` | Run full test suite, read output, confirm with evidence before claiming done                          |

### Parallel Independent Tasks

When facing 2+ independent problems (e.g., multiple unrelated test failures):

- **Skill:** `superpowers:dispatching-parallel-agents`
- Dispatch one focused subagent per problem domain, review and integrate results

### Documentation & API Lookup

When working with libraries, frameworks, or APIs:

- **Skill:** `context7-mcp` — Fetch current documentation via MCP instead of relying on training data
- Use for: Next.js, Supabase, Tailwind, FastAPI, SBERT, pgvector, or any library/framework question

---

## Quality Gates

### Before Writing Any Code

- **REQUIRED:** `superpowers:test-driven-development` — RED → GREEN → REFACTOR. No exceptions.

### Before Claiming Completion

- **REQUIRED:** `superpowers:verification-before-completion` — Run verification commands, read output, provide evidence. No "should work" or "looks correct."

### Before Merging

- **REQUIRED:** `superpowers:requesting-code-review` — Dispatch reviewer subagent with git SHAs.

---

## ECC Domain Skills (Use When Relevant)

| Skill                     | When to Use                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `ecc:coding-standards`    | Writing or reviewing any code                                |
| `ecc:backend-patterns`    | API routes, database queries, caching                        |
| `ecc:frontend-patterns`   | React components, Next.js pages, state management            |
| `ecc:api-design`          | Designing REST endpoints, pagination, error responses        |
| `ecc:postgres-patterns`   | Writing or optimizing Supabase/PostgreSQL queries            |
| `ecc:database-migrations` | Schema changes, data migrations                              |
| `ecc:security-review`     | Auth, user input handling, API endpoints, secrets            |
| `ecc:tdd-workflow`        | TDD methodology reference                                    |
| `ecc:verification-loop`   | Continuous verification patterns                             |
| `ecc:deployment-patterns` | CI/CD, Docker, health checks                                 |
| `ecc:docker-patterns`     | Containerization, Docker Compose                             |
| `ecc:e2e-testing`         | Playwright E2E test patterns                                 |
| `ecc:search-first`        | Research existing tools/libraries before writing custom code |

---

## Project-Specific Rules

- **CHED Compliance:** Never remove content from protected courses (CC101–CC106). Validate 146-unit floor.
- **Spec Location:** Design specs go to `docs/superpowers/specs/`. Implementation plans go to `docs/superpowers/plans/`.
- **Git Workflow:** Commit frequently with conventional commit messages. Feature work on branches, not main.
- **Python Backend:** Follow FastAPI patterns, type hints required, pytest for testing.
- **TypeScript Frontend:** Follow Next.js App Router conventions, `"use client"` on interactive pages.
- **Database:** Use Supabase client via Next.js API routes. Embeddings stored with pgvector. Follow `.agents/skills/supabase-postgres-best-practices/` for query optimization.
