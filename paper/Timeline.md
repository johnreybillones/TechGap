### **🗓️ Week 1: Foundation & Data Harvest**

**Goal:** Establish the "Lungs" of the system by building the ETL pipeline for both academic and market data.

* **Task 1.1: Database Setup (Supabase & pgvector):**  
  * Enable the pgvector extension to handle 384-dimensional SBERT embeddings.  
  * Execute the 3-table schema (jobs\_raw, curriculum\_tracks, skills\_library) to separate landing data from processed "Smart Data".  
  * Ensure jobs\_raw uses a JSONB column to preserve the full original response for auditing "hallucinated" skills later.  
* **Task 1.2: Adzuna FastAPI Service:**  
  * Implement a Python script using httpx to loop through Adzuna’s jobs/ph/search endpoint.  
  * Target 150 jobs per keyword across the 4 tracks (e.g., "Unity Developer" for CS-GD, "Cloud Engineer" for IT-NT) to reach the 1,500+ total dataset requirement .  
* **Task 1.3: Playwright Stealth Scrapers:**  
  * Configure a "Headless: False" scraper for Indeed and JobStreet to handle dynamic content like "Load More" buttons.  
  * Implement "Human-Mimicry Logic" using random delays (3–7 seconds) and wait\_for\_timeout to avoid IP bans .  
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
  * Generate 64-dim structural vectors using **Node2Vec** (or GCN) based on the skill's position in the ontology graph .  
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