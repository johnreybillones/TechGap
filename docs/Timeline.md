### **🗓️ Week 1: Foundation & Data Harvest**

**Goal:** Establish the "Lungs" of the system. Data collection runs **continuously throughout the project** — model pipeline work begins once the **1,500-job threshold** is reached (~3–4 days in). The **Apify JobStreet actor** is the primary collection tool (Playwright/Bright Data plan deprecated April 2026).

* **Task 1.1: Database Setup (Supabase & pgvector):**  
  * Enable the pgvector extension to handle 384-dimensional SBERT embeddings.  
  * Execute the 3-table schema (jobs\_raw, curriculum\_tracks, skills\_library) to separate landing data from processed "Smart Data".  
  * Ensure jobs\_raw uses a JSONB column to preserve the full original response for auditing "hallucinated" skills later.  
* **Task 1.2: Adzuna FastAPI Service (Supplement):**  
  * Run as a **one-time bulk pull** in the first 1–2 days to seed the dataset quickly.  
  * Use 12 track-specific keywords across the 4 tracks to pull all available PH listings (~1,000–1,500 jobs expected).  
  * Triggered automatically if JobStreet yield for a track falls below the **300-job per-track minimum**.  
* **Task 1.3: Apify JobStreet Actor — Primary Data Collection:** ✅ *Phases 1–3 complete (April 2026)*  
  * ~~Original plan: Playwright stealth scraper + Bright Data proxies~~ — **Replaced with Apify managed actor** (`shahidirfan/jobstreet-scraper`) due to Bright Data API access issues.  
  * Actor natively handles JavaScript rendering, Cloudflare bypass, and proxy rotation — zero manual anti-bot configuration required.  
  * **20 keywords** across 4 tracks, **250 jobs per keyword** = **5,000 target total**. Track breakdown: IT-WD (6 keywords ~1,500), IT-NT (5 ~1,250), CS-IS (5 ~1,250), CS-GD (4 ~1,000).  
  * ETL pipeline (`scraper/pipeline/ingest.py`) handles field mapping, salary regex parsing, local dedup by `external_id`, and Supabase upsert with `UNIQUE(source, external_id)` constraint.  
  * **Smoke test passed**: 20 jobs, 0 errors, 18.8s elapsed. Full-scale run (`--max 5000`) is the next step.  
  * Cost: ~$5 Apify free credit for the full 5,000-job collection.
* **Task 1.4: Curriculum PDF Parser:**  
  * Build a service to ingest PDF syllabi and extract the "Specialization" (e.g., CS-IS) and "Syllabus Text".  
  * Map the raw text into the curriculum\_tracks table for future vectorization.

---

### **🗓️ Week 2: The NLP Cleaning Engine**

**Goal:** Convert "messy" descriptions into structured skill hierarchies and seniority levels.

* **Task 2.1: Hybrid NER (Skill Extraction):**  
  * Use spaCy with EntityRuler to match terms against a **Master Skills List** (\~500 tech terms).  
  * Implement "Candidate Discovery" logic to extract Proper Nouns not in the list using spaCy's en\_core\_web\_md model.  
* **Task 2.2: Bloom’s Taxonomy Scorer:**  
  * Create a classifier to assign a level (1–6) to every extracted skill (e.g., "Remembering syntax" \= 1, "Architecting systems" \= 5).  
  * This data will eventually feed the **Cognitive Depth Analysis** heatmap on the dashboard.  
* **Task 2.3: Skill Ontology Mapping:**  
  * Build a JSON-based **Skill Ontology** graph that defines parent-child relationships (e.g., "NestJS" implies "Node.js" and "TypeScript").  
  * This graph allows the **Inference Engine** to filter out "false gaps" logically covered by advanced topics.  
* **Task 2.4: Data Cleaning & Seniority Extraction:**  
  * Apply spaCy pattern matching to job titles to extract seniority levels (Junior, Senior, Lead, Intern).  
  * Run global deduplication based on a hash of Title \+ Company \+ Location to ensure frequency data is accurate .

---

### **🗓️ Week 3: The Intelligence Layer**

**Goal:** Implement high-dimensional vector math and the logical reasoning core.

* **Task 3.1: Hybrid Vector Generation (SBERT \+ Node2Vec):**  
  * Generate 384-dim semantic vectors using the all-MiniLM-L6-v2 SBERT model .  
  * Generate 64-dim structural vectors using **Node2Vec** based on the skill's position in the ontology graph.  
* **Task 3.2: Concatenation & Storage:**  
  * Merge the two vectors into a single **448-dim Hybrid Embedding**.  
  * Upsert these into Supabase using pgvector indexed with HNSW for high-speed similarity searches .  
* **Task 3.3: The Inference Engine (Reasoning Core):**  
  * Build the "Dependency Mapper" that performs "Subsumption Reasoning".  
  * If a curriculum skill is a "descendant" of a job skill (or vice-versa), adjust the "Gap Score" to prevent redundant red flags.  
* **Task 3.4: Adaptive Ranking Engine (LTR):**  
  * Implement a **Learning-to-Rank** algorithm (e.g., XGBRanker) to prioritize gaps.  
  * Rank items by a composite score of **Industry Demand Weight** (frequency in scrapes), **Gap Severity** (vector distance), and **Bloom’s Level** .

---

### **🗓️ Week 4: Integration & Visualization**

**Goal:** Translate complex ML data into an actionable dashboard for curriculum developers.

* **Task 4.1: Job Family Classifier:**  
  * Train a **Logistic Regression** model to predict which of the 8 job "Families" (e.g., "Web Frontend") a curriculum belongs to based on its vector.  
  * This ensures the Inference Engine compares the curriculum against the correct domain.  
* **Task 4.2: Frontend Dashboard Development:**  
  * Build interactive components using React and Tailwind to display the **Alignment Score** and **Skill Badges** (Green/Yellow/Red) .  
  * Implement the **Cognitive Depth Heatmap** using the stored bloom\_distribution JSON data.  
* **Task 4.3: Action Plan Generator:**  
  * Display "Priority Recommendations" that quantify potential impact (e.g., "Adding Docker will increase alignment by 12%").  
  * List "True Gaps" filtered by the Inference Engine and sorted by the Ranking Engine.  
* **Task 4.4: End-to-End Validation:**  
  * Run a full system test: Upload a PDF $\\rightarrow$ Parse $\\rightarrow$ Hybrid Vectorize $\\rightarrow$ Inference Filter $\\rightarrow$ Rank $\\rightarrow$ Dashboard Display .  
  * Verify the final JSON output contains alignment\_score, job\_family, and missing\_skills\_ranked .


1. 