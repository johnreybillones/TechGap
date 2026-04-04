# TechGap PRD

## **1. Input Specifications (The Data Foundation)**

The system requires two distinct data streams to function. Developers must ensure these properties are present and validated before they hit the model.

### **A. Curriculum Data**

- **Source:** PDF (Syllabus/Course Outline).
- **Regulatory Basis:** CHED CMO No. 25, Series of 2015 — defines the minimum standards, required core courses, and outcomes for BSCS/BSIT programs.
- **Properties to Extract:**
  - **Specialization**: A mandatory identifier (e.g., `CS-IS`, `CS-GD`) used by the Job Family Classifier (Task 4.1) to filter the relevant job market clusters for comparison.
  - **Program Type**: `BSCS` or `BSIT` — determines thesis vs. capstone requirements and applicable CHED outcomes (CS01–CS10 vs. IT01–IT10).
  - **Course Title**: Provides hierarchical context.
  - **Course Code**: The institutional identifier (e.g., `IT 321`, `CC104`).
  - **Course Type**: `core`, `professional`, `elective`, or `GE` — determines how aggressively the system can suggest modifications (see Section 3.D).
  - **CHED Protected Status**: Boolean flag for the 6 mandated common courses (CC101–CC106). The system can only suggest *additions* to protected courses, never removals.
  - **Units**: Credit units per course — used to enforce the 146-unit minimum floor.
  - **Hours Per Week**: Contact hours — enables time-specific suggestions like "replace 2-week VMware unit."
  - **Syllabus Text**: The raw body used for SBERT embeddings.
  - **Skill Keywords**: Identified technical competencies.
  - **Course Level**: (Introductory, Intermediate, Advanced) to correlate with Bloom's Taxonomy.

### **B. Job Market Data (Industry Pulse)**

- **Primary Source:** Playwright Scraper (JobStreet Philippines) — high-quality, structured data extracted from `__NEXT_DATA__` JSON.
- **Supplementary Source:** Adzuna API (`jobs/ph/search`) — used as a fast-burst supplement when JobStreet yield falls below the per-track minimum, or to accelerate collection in Week 1.
- **Collection Strategy:** Data collection runs **continuously in the background** throughout the project. Model pipeline work begins once a minimum batch of **1,500 jobs** is available. Final model evaluation uses the full dataset collected by Week 4.
- **Target:** **5,000 unique job postings** (minimum viable); 10,000 is a stretch goal.
- **Scope:** Philippines only, ICT/IT classification, posted within the last 6 months, English language, deduplicated by `external_id`.
- **Properties to Extract:**
  - **Job Title**: The specific name of the role (e.g., "Full Stack Developer").
  - **Contract Type:** Extracted from source (e.g., Full-time, Contract, Part-time).
  - **Seniority Level:** Extracted via NLP (e.g., Junior, Senior, Lead, Intern). Used for K-Means clustering.
  - **Job Description**: The source for semantic matching and SBERT embedding.
  - **Skill Keywords**: Extracted technical competencies from the job posting.
  - **Industry Demand Frequency**: How often a skill appears (feeds the Ranking Engine).
  - **Location/Salary**: Contextual metadata for the Philippines market.

### **C. Knowledge & Framework Data (The Intelligence)**

- **Skill Ontology:** A JSON/RDF graph of ~500 skills with parent-child relationships (e.g., React → JavaScript → Programming). Used by the Inference Engine to detect logically-covered skills.
- **Suggested Topics:** Pre-curated 3–5 sub-topic breakdowns per skill stored in `skills_library.suggested_topics`. Used to generate specific course modification suggestions without AI API calls.
- **Program Outcomes:** CHED-mandated program outcomes (CS01–CS10, IT01–IT10) mapped to each skill in `skills_library.program_outcomes`. Used to validate that every suggestion contributes to at least one required outcome.
- **Bloom's Taxonomy Metadata:** Classification of skills into cognitive levels (L1–L6).

---

## **2. Process Specifications (The Engine & Stack)**

### **A. The Algorithm Pipeline**

The model doesn't just "match" words; it follows a logical sequence to determine "True Gaps."

1. **Vectorization (SBERT + Node2Vec):** Converts raw text and the skill ontology graph into 448-dim "Hybrid Embeddings" (384 SBERT + 64 Node2Vec).
2. **Clustering (K-Means):** Groups jobs into families using Title and Seniority Level metadata. A **Logistic Regression** classifier then maps each curriculum to its relevant family.
3. **Inference Engine (Reasoning):** Uses the Skill Ontology Knowledge Graph to filter out skills logically covered by advanced topics (e.g., React covers JavaScript).
4. **Adaptive Ranking (LambdaMART/XGBRanker):** Sorts gaps based on Market Demand, Gap Severity, and Bloom's Taxonomy Level.
5. **Course Anchoring (Cosine Similarity):** For each ranked gap skill, computes cosine similarity against all `curriculum_courses.embedding` to identify the best existing course to absorb the gap, or determines a new course is needed (see Section 3.B.2).
6. **CHED Constraint Validation:** Every suggestion passes through regulatory guardrails before being presented to the user (see Section 3.D).

### **B. The Tech Stack**

- **Frontend (Next.js + TypeScript + Tailwind):** Handles file uploads, progress bars for scrapers, and the interactive gap dashboard. Uses the App Router with `"use client"` on dashboard pages. API routes (`/api/*`) proxy calls to FastAPI to avoid exposing backend credentials on the client.
- **Backend (FastAPI):** Orchestrates the ETL pipeline, runs the Python-based ML models, executes the course-anchoring computation, and generates CHED-validated suggestion reports.
- **Database (Supabase + pgvector):** Stores raw jobs, curriculum metadata, skill ontology, and the mathematical vectors for high-speed similarity searches. Free tier (500 MB) is sufficient for 5K–10K jobs.

---

## **3. Output Specifications (The User Dashboard)**

The dashboard translates ML results into **actionable curriculum decisions**. Outputs are structured in 5 tiers, from high-level overview to detailed revision instructions. All computations are deterministic (cosine similarity, SQL aggregation, threshold rules) — no AI API calls required.

> 📄 **For field-level specs, decision logic tables, and example outputs, see [PRD_Detailed.md](./PRD_Detailed.md).**

### **A. Tier 1 — Track-Level Alignment Dashboard**

A health check per specialization track showing: alignment score (%), skill coverage breakdown (matched/inferred/missing), Bloom's depth distribution (L1–L6), and the top 3 gap skills with demand percentages.

### **B. Tier 2 — Course-Anchored Gap Report** *(Core Output)*

For each ranked gap skill, the system determines an **action type** based on cosine similarity to existing courses:

- **MODIFY** (similarity > 0.60) — Add the gap as a new module within an existing course.
- **ELECTIVE** (0.40–0.60) — Suggest a new elective course.
- **NEW COURSE** (< 0.40) — Recommend a fundamentally new course.

Each gap entry includes: urgency score, industry demand %, anchor course, specific topics to add (from `suggested_topics`), replacement candidates with demand ratios, Bloom's before/after projection, alignment delta, new job matches, and CHED program outcomes mapped.

### **C. Tier 3 — Obsolescence Detection**

Flags topics with industry demand below the 5th percentile and suggests higher-demand replacements within the same skill category. Each entry shows the current vs. replacement demand ratio and CHED protection status.

### **D. Tier 4 — Course-to-Job Role Mapping**

Maps each course to the job roles it currently prepares students for (via cosine similarity to `jobs_raw`), then projects which **new roles become accessible** after implementing suggested changes. Shows before/after job title counts.

### **E. Tier 5 — Curriculum Revision Summary Report**

A printable executive summary for the Academic Council containing: current alignment state, priority-sorted recommended changes, projected post-revision alignment, obsolescence report, CHED compliance verification (146-unit floor, protected courses, outcome mapping), and faculty qualification warnings.

### **F. CHED Compliance Guardrails**

Every suggestion passes through 6 hard constraints before being shown to the user:

1. **Protected Courses** — CC101–CC106 can only receive additions, never removals.
2. **146-Unit Floor** — New course suggestions validate that total units remain ≥ 146.
3. **Flexibility Hierarchy** — Modifications prefer: elective > professional > core > GE.
4. **Program Outcome Mapping** — Every suggestion must map to at least one CHED outcome (CS01–CS10 / IT01–IT10).
5. **Thesis vs. Capstone** — BSCS tracks prioritize research alignment; BSIT tracks prioritize applied skills.
6. **Faculty Warnings** — Flags when a suggestion introduces a skill category with no existing faculty coverage.

---

## **4. Developer "Source of Truth" Checklist**

- \[ \] **Stealth Check:** Are the Playwright scrapers using random delays to avoid IP bans?
- \[ \] **Vector Check:** Are we storing SBERT embeddings in the pgvector column in Supabase?
- \[ \] **Inference Check:** Does the model understand that a "React" course doesn't need to be told it also teaches "JavaScript"?
- \[ \] **Ranking Check:** Is the "Missing Skills" list sorted by market frequency, not alphabetically?
- \[ \] **CHED Check:** Does the system prevent removal of CC101-CC106 content? Does it validate the 146-unit floor before suggesting new courses?
- \[ \] **Course Anchoring Check:** Are gap skills mapped to specific courses via cosine similarity, not just listed as abstract skill names?
- \[ \] **Suggested Topics Check:** Does every skill in `skills_library` have a `suggested_topics` JSONB with 3–5 sub-topic breakdowns?
- \[ \] **Output Check:** Does the dashboard show all 5 tiers (Alignment + Course-Anchored Gaps + Obsolescence + Job Mapping + Summary Report)?
