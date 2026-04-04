# TechGap PRD — Detailed Output Specifications

> This document is the **technical companion** to [PRD.md](./PRD.md). It contains the full field-level specifications, decision logic, computation methods, and example outputs for each of the 5 output tiers. Developers should reference this when implementing the FastAPI inference endpoints and the React dashboard components.

---

## **Tier 1 — Track-Level Alignment Dashboard**

The first thing users see: a health check for each curriculum specialization track.

**What it shows:**

- **Alignment Score:** A percentage representing the cosine similarity between the track's hybrid embedding and the centroid of its matched job cluster. Example: `IT-NT: 67% aligned`.
- **Skills Breakdown:** Counts of skills explicitly matched (Green), inferred/logically covered (Yellow), and truly missing (Red).
- **Bloom's Depth Bar:** A horizontal stacked bar showing the track's Bloom's distribution (L1–L6 counts from `curriculum_courses.bloom_level`).
- **Top 3 Gaps:** The highest-ranked True Gap skills with their industry demand percentages.
- **Strongest/Weakest Subtopics:** Which skill categories within the track are best covered vs. most deficient.

**How it's computed:** Fully deterministic — cosine similarity on `curriculum_tracks.hybrid_embedding` vs. centroid of `jobs_raw.description_embedding` for that track, SQL aggregation on `job_skills` and `curriculum_courses`.

---

## **Tier 2 — Course-Anchored Gap Report**

The core output. For each True Gap in the ranked list, the system identifies **which specific course** should absorb it, or whether a new course is needed.

### **The Decision Logic**

For each ranked gap skill, the backend computes cosine similarity between `gap_skill.embedding` and every `curriculum_courses.embedding` in the target track:

| Similarity Score | Action Type | Meaning |
|---|---|---|
| **> 0.60** | **MODIFY** (Enhance existing course) | The gap skill is *adjacent* to this course's content — add it as a new module within the existing course. |
| **0.40 – 0.60** | **ELECTIVE** (Suggest new elective) | The skill is loosely related but doesn't fit cleanly in any existing course — recommend a new elective. |
| **< 0.40** | **NEW COURSE** (Create new course) | Nothing in the curriculum is close enough — this requires a fundamentally new course. |

The system also applies the **CHED flexibility hierarchy** to prefer anchoring gaps to courses where modification is safest:

```
Elective (full freedom) > Professional (moderate) > Core (additions only) > GE (untouchable)
```

### **Information Per Gap**

Each gap entry in the report includes:

| Field | Source | Example |
|---|---|---|
| **Gap Skill Name** | `skills_library.skill_name` | Docker & Containerization |
| **Urgency Score** | XGBRanker output (0–1) | 0.92 |
| **Industry Demand %** | `skills_library.industry_demand_weight` × 100 | 43% of IT-NT jobs |
| **Bloom's Level** | `skills_library.bloom_level` | L3–L4 (Applying–Analyzing) |
| **Action Type** | Similarity threshold (see above) | MODIFY |
| **Anchor Course** | `argmax(cosine_similarity(gap.embedding, courses.embedding))` | IT 321 — Systems Administration |
| **Anchor Similarity** | Cosine similarity score | 0.72 |
| **Course Type** | `curriculum_courses.course_type` | Professional |
| **CHED Status** | `curriculum_courses.is_ched_protected` | ✅ Not protected |
| **Topics to Add** | `skills_library.suggested_topics` | ["Dockerfile syntax", "Docker Compose", "Kubernetes basics"] |
| **Replace Candidate** | Lowest `industry_demand_weight` topic in same course | "Desktop Virtualization (VMware)" — 8% demand |
| **Replace Rationale** | Demand ratio: `gap_demand / replaced_demand` | Docker demand is 5.4× higher than VMware desktop |
| **Bloom's Before/After** | `GROUP BY bloom_level` on anchor course | Before: L1(3) L2(5) L3(2) L4(0) → After: L1(3) L2(4) L3(4) L4(1) |
| **Alignment Delta** | Re-compute alignment with gap skill virtually added | +7pp (67% → 74%) |
| **New Job Matches** | Count of newly-matched jobs above similarity threshold | +215 postings |
| **Program Outcomes** | `skills_library.program_outcomes` | IT03 (Design Solutions), IT07 (Modern Tools) |
| **Alternative Courses** | 2nd and 3rd closest courses by similarity | IT 312 (0.58), IT 411 (0.41) |

### **Example Outputs**

#### Example 1: MODIFY an existing course

```
GAP #1: Docker & Containerization
Urgency: 0.92 │ Demand: 43% of IT-NT jobs │ Bloom: L3-L4

📌 ACTION: MODIFY existing course

Anchor Course: IT 321 — Systems Administration
Course Type: Professional │ CHED: ✅ Not protected

ADD Topics:
  • Dockerfile syntax & multi-stage builds (L3)
  • Container orchestration with Docker Compose (L3)
  • Introduction to Kubernetes pods & services (L4)

CONSIDER REPLACING:
  • "Desktop Virtualization (VMware Workstation)" — 8% demand
  • Rationale: Docker demand is 5.4× higher

BLOOM'S IMPACT:
  Before: L1(3) L2(5) L3(2) L4(0)
  After:  L1(3) L2(4) L3(4) L4(1) ─ shifts cognitive depth upward

ALIGNMENT IMPACT: 67% → 74% (+7pp), +215 job matches
CHED OUTCOMES: IT03, IT07 ✅
⚠️ Faculty Note: Verify DevOps/Cloud faculty qualifications (CMO §6.3)
```

#### Example 2: Suggest a NEW ELECTIVE

```
GAP #5: Cloud Architecture (AWS/Azure/GCP)
Urgency: 0.78 │ Demand: 38% │ Bloom: L5

📌 ACTION: NEW ELECTIVE

Nearest Course: IT 321 (similarity: 0.38 — too distant)

CREATE: "IT 4XX — Cloud Infrastructure & Architecture"
  Suggested Bloom Range: L3–L5
  Core Topics: IaaS/PaaS comparison, VPC design, auto-scaling, IaC

JUSTIFICATION:
  • No existing course scores above 0.40 similarity
  • 38% of IT-NT jobs require cloud architecture
  • Current track has ZERO Level 5 coverage
  
UNIT IMPACT: Must verify total track units remain ≥ 48 professional
CHED OUTCOMES: IT03, IT05, IT07 ✅
```

#### Example 3: ENHANCE a CHED-protected course

```
GAP #4: Advanced Data Structures (Red-Black Trees)
Urgency: 0.45 │ Demand: 12% │ Bloom: L4-L5

📌 ACTION: ENHANCE (CHED-protected course)

Anchor Course: CC104 — Data Structures and Algorithms
Course Type: Core (Common) │ CHED: 🔒 PROTECTED

ADD Topics (within existing time allocation):
  • Red-Black tree implementation exercise (L4)
  • Comparative analysis: BST vs AVL vs RB-tree (L5)

❌ CANNOT REPLACE any existing content.
Reason: CC104 is a CHED-mandated common course (CMO §5.1)
Consider adding as supplementary material or lab exercise.
```

---

## **Tier 3 — Obsolescence Detection**

Identifies topics currently consuming course time that have **low or declining industry demand**, making them candidates for replacement or reduction.

**What it shows per flagged topic:**

| Field | Source | Example |
|---|---|---|
| **Topic Name** | Nearest `skills_library.skill_name` to the course outcome embedding | jQuery DOM Manipulation |
| **Current Course** | `curriculum_courses.course_title` | IT 213 — Web Development Fundamentals |
| **Industry Demand** | `skills_library.industry_demand_weight` | 4% of IT-WD jobs |
| **Bloom Level** | `curriculum_courses.bloom_level` | L3 (Applying) |
| **Suggested Replacement** | Highest-demand gap skill in the same `skills_library.category` | React Fundamentals (62% demand) |
| **Demand Ratio** | Replacement demand / current demand | React is 15.5× higher demand |
| **CHED Status** | `is_ched_protected` | ✅ Not protected — can be replaced |
| **Suggestion** | Template-based | "Replace jQuery unit with React fundamentals. jQuery can remain as a 1-hour historical reference." |

**How it's computed:** For each `curriculum_courses.embedding`, find the nearest skill in `skills_library`. If `industry_demand_weight < 0.05` (bottom 5th percentile of all skills), flag the topic as low-demand.

---

## **Tier 4 — Course-to-Job Role Mapping**

Shows which specific job roles each course currently prepares students for, and which new roles become accessible after implementing the suggested changes.

**What it shows per course:**

| Field | Computation | Example |
|---|---|---|
| **Current Job Roles** | Top-K similar `jobs_raw` to `course.embedding`, grouped by `job_title` | Frontend Developer (72%), Web Designer (68%) |
| **Match Percentage** | Cosine similarity averaged across job cluster | 72% |
| **Projected Job Roles (after changes)** | Re-run top-K with modified embedding (original + gap skill averaged) | React Developer (89%) ← NEW, Full Stack Dev (64%) ← NEW |
| **New Roles Unlocked** | Count of job titles not in current mapping | +2 categories |
| **New Job Postings Matched** | Count of `jobs_raw` rows above similarity threshold | +340 postings |

**How it's computed:** Fully deterministic — pgvector cosine similarity on `jobs_raw.description_embedding`, then SQL `GROUP BY job_title`.

---

## **Tier 5 — Curriculum Revision Summary Report**

A printable executive summary for the Academic Council — the document a dean hands to the curriculum committee.

**Contents:**

1. **Current State:** Overall alignment score, total skills covered/missing, Bloom's distribution summary.
2. **Recommended Changes (priority-sorted):**
   - For each change: action type (MODIFY/NEW/ENHANCE), target course, topics to add, topics to replace, alignment delta, Bloom's shift, CHED compliance status, program outcomes mapped.
3. **Projected State (after all changes):** New alignment score, new skill coverage, new Bloom's distribution, new job roles accessible.
4. **Obsolescence Report:** Topics flagged for reduction/removal with demand data.
5. **CHED Compliance Summary:** Verification that all changes maintain ≥ 146 units, no protected courses were violated, all new suggestions map to at least one program outcome.
6. **Faculty Qualification Warnings:** Any suggestions that may require faculty with new specializations (CMO §6.3).

**How it's computed:** Aggregation of Tiers 1–4. All data points come from prior computations. The report is generated using Python string templates (f-strings) in the FastAPI backend — no AI API calls required.

---

## **CHED Compliance Guardrails (Hard Constraints)**

Every suggestion generated by the system must pass through these regulatory checks before being presented to the user. These are non-negotiable constraints derived from **CHED CMO No. 25, Series of 2015**.

| Constraint | Rule | Implementation |
|---|---|---|
| **Protected Courses** | CC101–CC106 cannot have content removed or significantly diluted | If `is_ched_protected = TRUE`, action type is forced to `ENHANCE` (additions only) |
| **146-Unit Floor** | Total curriculum units must remain ≥ 146 (or the institution's actual total) | Validate `SUM(units)` from `curriculum_courses` before suggesting new courses |
| **Course Type Flexibility** | Modifications prioritized by flexibility: elective > professional > core > GE | Course anchoring prefers higher-flexibility courses when similarity scores are comparable (±0.05) |
| **Program Outcome Mapping** | Every new course or major topic addition must map to at least one CHED outcome | `skills_library.program_outcomes` is checked; suggestions without mappings get a warning |
| **Thesis vs. Capstone** | BSCS tracks → research/theory alignment; BSIT tracks → applied/infrastructure alignment | `curriculum_tracks.program_type` determines which job families and Bloom's levels are prioritized |
| **Faculty Qualification Warning** | If a suggested skill's `category` doesn't match any existing course's category in that track, emit a faculty qualification warning | Compare `skills_library.category` against unique categories in `curriculum_courses` for that track |
