# TechGap - Technical Plan Status

> **Last Updated:** 2026-05-13
> **Purpose:** Master technical readiness document for the TechGap v1 role-based flow.
> Cross-referenced by: `use_case.md`, `PRD.md`, `PRD_Detailed.md`, `Model.md`, `ALGORITHMS.md`

> **Readiness standard used in this file:**
> A use case is marked `OK Fully Planned` when its v1 behavior, core data shape, validation rules, algorithm approach, and feasible UI/API boundary are specified well enough for downstream PRD and implementation work. Final visual UI design may still be deferred.

> **Legend:**
> - OK **Fully Planned** - v1-ready technical direction is defined.
> - PARTIAL **Partially Planned** - technically feasible, but one or more core decisions still need to be locked.
> - TODO **Planned / To Specify** - belongs in v1 but has no implementation-ready technical definition yet.
> - DEFERRED **Deferred** - intentionally outside v1 scope.

---

## Summary Table

| Use Case | Actor | Functional Spec | Technical Plan | Overall Status |
|---|---|---|---|---|
| Choose Role | Both | OK | OK | OK Fully Planned |
| Select Program and Year Level | Student | OK | OK | OK Fully Planned |
| Select Mastered Courses | Student | OK | OK | OK Fully Planned |
| Choose Career Role / Top 5 Suggestions / Other Career Option | Student | OK | OK | OK Fully Planned |
| Run Personal Alignment Analysis | Student | OK | OK | OK Fully Planned |
| View Skill Gap Report (Personal) | Student | OK | OK | OK Fully Planned |
| Use Skill Roadmap | Student | OK | OK | OK Fully Planned |
| Browse Node Resources | Student | OK | OK | OK Fully Planned |
| Select Curriculum Track | Admin/Faculty | OK | OK | OK Fully Planned |
| View Top 5 Jobs | Admin/Faculty | OK | OK | OK Fully Planned |
| Review Job Evidence | Admin/Faculty | OK | OK | OK Fully Planned |
| View Alignment Dashboard | Admin/Faculty | OK | OK | OK Fully Planned |
| View Gap and Obsolescence Report | Admin/Faculty | OK | OK | OK Fully Planned |
| Generate Curriculum Report | Admin/Faculty | OK | OK | OK Fully Planned |
| Authentication / RBAC | Both | DEFERRED | DEFERRED | DEFERRED Not a v1 blocker |
| Syllabus Upload UI | Admin/Faculty | DEFERRED | DEFERRED | DEFERRED Not a v1 blocker |
| Interactive Curriculum Simulation | Admin/Faculty | DEFERRED | DEFERRED | DEFERRED Outside main v1 flow |

---

## v1 Scope Decisions

### No-auth entry point

TechGap v1 starts at a no-auth **Choose Role** screen. Authentication, registration, and RBAC are deferred so the student and admin/faculty flows can ship without identity infrastructure as a blocker.

### Route architecture

The frontend route shape is fixed as:

- `/` - Choose Role
- `/student` - Student flow
- `/admin` - Admin/Faculty flow

Role switching from `/student` or `/admin` returns the user to `/` and clears role-specific transient state.

### API boundary

The public frontend boundary is Next.js API routes under `/api/*`. These routes proxy to FastAPI endpoints under `/v1/*`.

This keeps browser clients decoupled from backend service topology and preserves a clean future path for auth, caching, and request shaping.

### Curriculum source

Curriculum content is preloaded from structured CSVs for the supported tracks:

| Track | Program Focus |
|---|---|
| `CS-IS` | Computer Science - Intelligent Systems |
| `CS-GD` | Computer Science - Game Development |
| `IT-WD` | Information Technology - Web Development |
| `IT-NT` | Information Technology - Network Technology |

Syllabus parsing remains a data-preparation concern, not a user-facing v1 flow.

### Student persistence

Student selections persist in browser `localStorage`, not in a user table or backend session.

- Storage is versioned, for example: `techgap.student.v1`
- Stored fields include program, year level, selected mastered courses, selected role, and latest analysis payload metadata if needed
- Data resets when the student clicks a Reset action or intentionally switches role

### Ranking baseline

`TOPSIS` is the v1 deterministic ranking method where ranking is needed without expert labels. `XGBRanker` remains a v2 upgrade path after enough labeled data exists.

### Admin report framing

Admin/faculty v1 is report-centered. Alignment delta, gap outputs, obsolescence findings, and recommendation summaries remain in v1, but the old standalone what-if simulation workflow is deferred.

---

## Shared Use Cases

### UC-SHARED-1 - Choose Role

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 6 |
| **Technical Plan** | OK Separate routes and reset behavior defined |

**Planned behavior:**
- Show `Student` and `Admin/Faculty` as the only entry choices.
- Route `Student` to `/student` and `Admin/Faculty` to `/admin`.
- Clear role-specific transient state when the user intentionally switches role.

**Validation and state rules:**
- No role selected: remain on `/`.
- Invalid direct access to role pages without minimal required state falls back to that flow's first step, not an auth gate.

---

## Student Use Cases

### UC-S1 - Select Program and Year Level

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 3 |
| **Technical Plan** | OK Program/year model, filtering rule, and persistence defined |

**Planned behavior:**
- Student selects program: `CS` or `IT`.
- Student selects year level: `1st`, `2nd`, `3rd`, `4th`, or `Irregular`.
- This context controls which curriculum courses are displayed for mastery selection.

**Filtering rule:**
- `1st` to `4th`: show all courses in the selected program up to the selected year level.
- `Irregular`: show all courses in the selected program grouped by year.

**Persistence:**
- Program and year level are stored in browser `localStorage`.

**Validation:**
- Program is required.
- Year level is required.
- Changing program clears selected mastered courses and selected role because downstream analysis assumptions change.

---

### UC-S2 - Select Mastered Courses

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 3 |
| **Technical Plan** | OK Selection semantics, state shape, and weighting basis defined |

**Meaning of "mastered":**
- A selected course is either completed or confidently mastered by the student.
- v1 does not model per-skill confidence or transcript-grade validation.

**Planned behavior:**
- Show filtered courses from UC-S1.
- Allow multi-select of mastered courses.
- Use selected courses as the student's academic baseline for downstream analysis.

**Client state shape:**

```ts
type StudentSelectionState = {
  program: "CS" | "IT";
  yearLevel: "1st" | "2nd" | "3rd" | "4th" | "Irregular";
  masteredCourseCodes: string[];
  selectedCareerRoleId: string | null;
};
```

**Validation:**
- Selected courses must belong to the filtered program course set.
- Empty selection is allowed for exploration, but the career suggestion and analysis endpoints must return a sparse-evidence warning.

**Analysis basis:**
- Each selected course contributes to the student profile vector.
- Default weighting uses course units and Bloom depth so heavier and cognitively deeper courses matter more than light survey content.

---

### UC-S3 - Choose Career Role / Top 5 Suggestions / Other Career Option

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 3 |
| **Technical Plan** | OK Curated role taxonomy, ranking inputs, and selection flow defined |

**Planned behavior:**
- All students receive top 5 curated career-role suggestions after selecting mastered courses.
- Students may choose one of the suggested roles or another eligible scraped-job-backed career option as the analysis target.
- If the student's intended career is not in the top 5, the student may choose another eligible career option as long as it exists within the scraped job dataset and has supporting job evidence.
- Suggestions are career roles, not specialization-track labels.

**Role taxonomy decision:**
- Recommended top 5 roles come from a curated versioned catalog, not raw job titles.
- Each curated role has a stable ID, display name, allowed programs, related tracks, representative skills, and mapped job clusters.
- The alternate career option is not free text. It must resolve to a scraped-job-backed role or job-title group with enough evidence to build a role demand profile.

**Open cross-program rule:**
- Suggestions may cross the nominal CS/IT track boundary if the mastered-course evidence supports them.
- The selected program still controls course filtering, but does not hard-block role discovery.

**Top 5 suggestion summary formula:**
- Build student profile vector from mastered courses.
- Compare it against each eligible career-role demand profile.
- Combine:
  - semantic similarity to role profile
  - role demand weight from job data
  - evidence confidence from supporting job cluster coverage
- Rank descending and return top 5 recommended roles.

**Other-career selection rule:**
- The UI may expose a search or browse control for careers outside the top 5.
- Eligible options must come from the scraped jobs dataset or a role catalog mapped to scraped job clusters.
- The selected option must have a demand profile derived from the supporting scraped postings before personal alignment analysis can run.

**Fallback behavior:**
- If course evidence is sparse, still return 5 roles but flag the result as low-confidence.
- Ties are broken by demand weight, then by evidence count, then by stable role ID.

---

### UC-S4 - Run Personal Alignment Analysis

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 3 |
| **Technical Plan** | OK Student profile scoring model, endpoint boundary, and output shape defined |

**Planned behavior:**
- Build a student profile representation from mastered courses.
- Compare it against the selected career role's demand-weighted profile, whether the role came from the top 5 suggestions or the scraped-job-backed alternate option list.
- Return alignment score, gap categories, and supporting evidence.

**Student profile vector summary formula:**
- For each mastered course, compute or load its hybrid embedding.
- Weight each course by:
  - normalized units or contact-hours weight
  - normalized Bloom depth weight
- Average into one student profile vector.

**Alignment summary formula:**
- `personal_alignment = cosine_similarity(student_profile_vector, role_demand_profile)`
- The score is returned as a percentage for display.

**Score bands:**
- `>= 75%` - Strong alignment
- `50% to < 75%` - Moderate alignment
- `< 50%` - Weak alignment

**Future-course handling:**
- Skills already covered by future or unmastered courses in the student's curriculum are tracked separately as `Future Curriculum Coverage`.
- They are not merged into true missing gaps.

---

### UC-S5 - View Skill Gap Report (Personal)

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 3 |
| **Technical Plan** | OK Personal gap thresholds and category behavior defined |

**Planned behavior:**
- Show role-required competencies grouped into:
  - `Present`
  - `Partial`
  - `Missing`
  - `Future Curriculum Coverage`

**Threshold summary:**
- `Present`: similarity `>= 0.60`
- `Partial`: similarity `>= 0.40` and `< 0.60`
- `Missing`: similarity `< 0.40`

**Inference override:**
- If ontology traversal shows a logically related parent or child skill already covered, the skill may be upgraded from `Missing` to `Partial` or `Present` depending on the similarity evidence.

**Display requirements:**
- Each skill should show demand weight, evidence source, and explanation of why it landed in that category.
- Future-covered skills should identify the later course(s) that may close the gap.

---

### UC-S6 - Use Skill Roadmap

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 3 |
| **Technical Plan** | OK Node schema and sequencing logic defined |

**Planned behavior:**
- Convert prioritized gaps into a sequenced roadmap.
- Present it as ordered nodes with visible prerequisite relationships.

**Roadmap node schema:**

```ts
type RoadmapNode = {
  skillId: string;
  skillName: string;
  priorityScore: number;
  category: "Missing" | "Partial" | "Future Curriculum Coverage";
  prerequisiteSkillIds: string[];
  estimatedBloomLevel: number;
  demandWeight: number;
};
```

**Sequencing summary formula:**
- Start from the student's ranked personal gaps.
- Use TOPSIS urgency or equivalent deterministic priority score.
- Apply prerequisite ordering using skill-ontology relationships.
- When two nodes are independent, sort by higher urgency first.

**Progress behavior:**
- v1 roadmap progress is browser-local only.

---

### UC-S7 - Browse Node Resources

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 3 |
| **Technical Plan** | OK Cached resource strategy, trust model, and refresh rules defined |

**Planned behavior:**
- Resources load only when a roadmap node is opened.
- The student sees cached trusted resources immediately.
- Background refresh updates cached metadata without blocking the UI.

**Resource strategy:**
- Curated cache plus background metadata refresh.
- Source discovery is constrained by an allowlist of trusted domains.

**Trusted-source rule:**
- Accept resources only from approved domains such as official docs, MDN, roadmap.sh, The Odin Project, freeCodeCamp, or comparable curated sources approved later.

**Refresh rule:**
- v1 refresh updates metadata only: title, description, tags, accessibility, freshness, and availability.
- v1 does not auto-discover new links from the open web.

**Resource filters:**
- Skill relevance
- Beginner/intermediate suitability
- Free or accessible preference
- Active link availability

---

## Administrator / Faculty Use Cases

### UC-A1 - Select Curriculum Track

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 4 |
| **Technical Plan** | OK Track model and entry behavior defined |

**Planned behavior:**
- User selects one of: `CS-IS`, `CS-GD`, `IT-WD`, `IT-NT`.
- This track scopes all downstream admin analysis.

**Validation:**
- Unsupported or unloaded track returns an empty-state response, not a crash.

---

### UC-A2 - View Top 5 Jobs

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 4 |
| **Technical Plan** | OK Ranking inputs, evidence threshold, and list fields defined |

**Planned behavior:**
- Show the five most relevant jobs for the selected track.
- Each job card links to evidence review.

**Top-job summary formula:**
- Rank by a deterministic combination of:
  - curriculum-to-job similarity
  - demand weight or posting frequency
  - evidence confidence

**Evidence threshold:**
- A job must have at least 3 deduplicated postings to appear without a low-confidence flag.

**Job card fields:**
- role title
- demand weight
- skill overlap summary
- evidence count
- confidence flag if evidence is sparse

---

### UC-A3 - Review Job Evidence

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md` section 4 |
| **Technical Plan** | OK Evidence payload and display rules defined |

**Planned behavior:**
- Opening a top job reveals the evidence behind the role-track association.

**Evidence panel fields:**
- representative job title
- deduplicated posting count
- extracted skills
- demand signals
- matched cluster or role rationale
- source links or source identifiers where policy allows

**Sorting rule:**
- Show strongest evidence first by confidence, then demand, then recency if available.

---

### UC-A4 - View Alignment Dashboard

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `use_case.md`, `PRD.md`, `PRD_Detailed.md` |
| **Technical Plan** | OK Distinct metric definitions and endpoint boundary defined |

**Dashboard metrics planned for v1:**

| Metric | Definition |
|---|---|
| **Job Coverage Score** | Ratio-based primary admin metric measuring how many required skills from the top track-relevant jobs are covered by the full selected curriculum track after inference. |
| **Curriculum Relevance Score** | Ratio-based primary admin metric measuring how much of the full selected curriculum track's extracted skill inventory is directly relevant to the target job set. |

**Metric distinction:**
- `Job Coverage Score` is a coverage metric.
- `Curriculum Relevance Score` is a curriculum-efficiency and anti-bloat metric.

These are the two primary admin dashboard metrics.

**Full-curriculum assumption:**
- Admin/faculty analysis evaluates the full curriculum track and assumes students complete that curriculum.
- These admin metrics are not personalized by student year level, irregular status, or mastered-course subset.

**Supporting metric note:**
- A semantic similarity indicator may still be shown as a secondary supporting metric, but it does not replace the two primary ratio-based admin metrics.

---

### UC-A5 - View Gap and Obsolescence Report

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `PRD.md`, `PRD_Detailed.md` |
| **Technical Plan** | OK Existing algorithm flow remains valid for v1 |

**Planned behavior:**
- Show ranked true gaps, action type, anchor course, and obsolescence findings.
- Keep low-demand curriculum topics separate from high-priority market gaps.

---

### UC-A6 - Generate Curriculum Report

| Field | Status |
|---|---|
| **Overall Status** | OK Fully Planned |
| **Functional Spec** | OK `PRD.md`, `PRD_Detailed.md` Tier 5 |
| **Technical Plan** | OK Report aggregation remains the v1 admin terminal output |

**Planned behavior:**
- Aggregate dashboard, gap, obsolescence, and recommendation outputs into a printable report.
- Keep approval workflow outside v1.

---

## Endpoint Plan

The frontend-facing routes are fixed as:

| Frontend Route | Method | Purpose |
|---|---|---|
| `/api/student/courses` | `GET` | Return program-filtered courses for the selected year level |
| `/api/student/career-suggestions` | `POST` | Return top 5 recommended career-role suggestions plus eligible scraped-job-backed alternatives |
| `/api/student/analyze` | `POST` | Return personal alignment score and personal gap report |
| `/api/student/roadmap` | `POST` | Return ordered roadmap nodes for the selected role and gap profile |
| `/api/resources` | `GET` | Return cached learning resources for one roadmap skill |
| `/api/admin/tracks` | `GET` | Return available curriculum tracks |
| `/api/admin/top-jobs` | `GET` | Return top 5 jobs for a selected track |
| `/api/admin/job-evidence` | `GET` | Return evidence for one selected top job |
| `/api/admin/dashboard` | `GET` | Return dashboard metrics and supporting summaries |
| `/api/admin/report` | `GET` | Return printable curriculum report payload |

FastAPI mirrors these under `/v1/*` as the backend analysis boundary.

---

## Infrastructure & Backend Technical Plan Status

### Algorithm Pipeline

| Component | Status | Document Reference |
|---|---|---|
| Skill Extraction | OK Fully Planned | `ALGORITHMS.md` Phase 1 |
| SBERT Embedding | OK Fully Planned | `ALGORITHMS.md` Phase 2A, `Model.md` |
| Node2Vec Graph Embedding | OK Fully Planned | `ALGORITHMS.md` Phase 2B, `Model.md` |
| Hybrid Embedding | OK Fully Planned | `ALGORITHMS.md` Phase 2, `PRD.md` |
| K-Means Job Clustering | OK Fully Planned | `ALGORITHMS.md` Phase 3A |
| Logistic Regression Classifier | OK Fully Planned | `ALGORITHMS.md` Phase 3B |
| Inference Engine | OK Fully Planned | `ALGORITHMS.md` Phase 4 |
| Gap Detection | OK Fully Planned | `ALGORITHMS.md` Phase 5 |
| Adaptive Ranking | OK Fully Planned | `ALGORITHMS.md` Phase 6 |
| Course Anchoring | OK Fully Planned | `ALGORITHMS.md` Phase 7 |
| CHED Compliance Engine | OK Fully Planned | `ALGORITHMS.md` Phase 8, `PRD.md` |
| Bloom's Taxonomy Scorer | OK Fully Planned | `ALGORITHMS.md` Bloom section |
| Seniority Level Extraction | OK Fully Planned | `ALGORITHMS.md` Seniority section |
| Student Partial-Curriculum Scoring | OK Fully Planned | Summary formula locked in this document |
| Top 5 Career-Role Suggestion and Other Career Option | OK Fully Planned | Summary formula and scraped-job-backed option rule locked in this document |
| Roadmap Sequencing | OK Fully Planned | Deterministic urgency plus prerequisite ordering |
| Resource Ranking / Filtering | OK Fully Planned | Cached allowlist strategy locked in this document |

---

### Data Layer

| Component | Status | Document Reference / Note |
|---|---|---|
| Supabase + pgvector | OK Fully Planned | `PRD.md` |
| `jobs_raw` table schema | OK Fully Planned | `PRD.md` |
| `skills_library` table schema | OK Fully Planned | `PRD.md` |
| `analysis_runs` output table | OK Planned | `PRD_Detailed.md` architecture note |
| `gap_results` output table | OK Planned | `PRD_Detailed.md` architecture note |
| `obsolescence_results` output table | OK Planned | `PRD_Detailed.md` architecture note |
| `job_role_mappings` output table | OK Fully Planned | `PRD_Detailed.md` Tier 4 |
| Preloaded curriculum CSVs | OK Fully Planned | v1 curriculum source |
| Role selection state | OK Fully Planned | frontend route and client state |
| Student mastered-course selection | OK Fully Planned | browser `localStorage` plus validated course codes |
| Student roadmaps | OK Fully Planned | browser `localStorage` and generated payload |
| Learning resources catalog/cache | OK Fully Planned | allowlisted cached catalog with metadata refresh |
| `users` table | DEFERRED | Auth/RBAC outside v1 |
| `student_courses` table | DEFERRED | Not needed for browser-local persistence |

---

### Frontend

| Component | Status | Note |
|---|---|---|
| Tech stack: Next.js + TypeScript + Tailwind | OK Planned | Existing PRD stack |
| API proxy routes | OK Planned | `/api/*` proxies to FastAPI `/v1/*` |
| Choose Role screen | OK Fully Planned | `/` route with role switch reset behavior |
| Student onboarding wizard | OK Fully Planned | program, year, mastered courses, role selection |
| Course filtering by year level | OK Fully Planned | up-to-year or all-program for irregular |
| Top 5 career-role suggestion UI | OK Fully Planned | suggestion list with low-confidence fallback and scraped-job-backed alternate selection |
| Personal analysis and gap report UI | OK Fully Planned | score bands plus four-category gap report |
| Roadmap UI | OK Fully Planned | ordered nodes with prerequisite edges |
| Lazy node resource browsing | OK Fully Planned | node click fetches cached resources |
| Admin track selector | OK Fully Planned | fixed four-track entry |
| Admin top 5 jobs and evidence review | OK Fully Planned | list view plus evidence panel |
| Admin dashboard and reports | OK Fully Planned | distinct metrics and report endpoint |
| Protected routes | DEFERRED | Auth/RBAC outside v1 |

---

## Deferred Features

The following remain intentionally outside v1:

- authentication and RBAC
- user accounts and backend student persistence
- syllabus upload as a user-facing feature
- standalone interactive curriculum simulation
- formal report approval workflow

---

## Feasibility Notes

- The v1 plan is feasible because it uses preloaded curriculum CSVs and existing or seeded job data.
- Browser-local student persistence reduces backend scope without blocking the student flow.
- Cached resources with metadata refresh keep roadmap interactions fast while preserving a future path to better curation.
- Open cross-program role suggestions and scraped-job-backed alternate career choices are acceptable because role selection is guidance-oriented, while curriculum filtering remains program-bound.
- Main implementation risks are still data quality, role-taxonomy curation, and keeping student outputs explainable, but the architecture and endpoint boundaries are now defined.

---

## Changelog

| Date | Version | Change | Author |
|---|---|---|---|
| 2026-05-13 | v1.3 | Added student option to choose a career outside the top 5 suggestions when the option is backed by scraped job evidence | Codex |
| 2026-05-13 | v1.2 | Converted the file from a coverage audit into the master v1 technical readiness document with locked routes, persistence, endpoint boundaries, student scoring summaries, resource strategy, and admin metric definitions | Codex |
| 2026-05-12 | v1.1 | Revised status for no-auth role selection, student onboarding, top 5 career-role suggestions, admin track review, preloaded curriculum CSVs, and report-focused admin flow | Codex |
| 2026-05-12 | v1.0 | Initial creation: full audit of all use cases vs. PRD/Model documentation | Previous agent |

---

*For functional scope, refer to [use_case.md](./use_case.md). For the synchronized product and algorithm revisions that follow from this file, refer to [PRD.md](./PRD.md), [PRD_Detailed.md](./PRD_Detailed.md), and [ALGORITHMS.md](./ALGORITHMS.md).*
