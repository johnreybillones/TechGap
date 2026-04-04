# TechGap PRD

## **1\. Input Specifications (The Data Foundation)**

The system requires two distinct data streams to function. Developers must ensure these properties are present and validated before they hit the model.

### **A. Curriculum Data**

- **Source:** PDF (Syllabus/Course Outline).
- **Properties to Extract:**
  - **Specialization**: A mandatory identifier (e.g., `CS-IS`, `CS-GD`) used by the Job Family Classifier (Task 4.1) to filter the relevant job market clusters for comparison.
  - **Course Title**: Provides hierarchical context.
  - **Syllabus Text**: The raw body used for SBERT embeddings.
  - **Skill Keywords**: Identified technical competencies.
  - **Course Level**: (Introductory, Intermediate, Advanced) to correlate with Bloom’s Taxonomy.

### **B. Job Market Data (Industry Pulse)**

- **Source:** Adzuna API \+ Playwright Scrapers (Indeed/JobStreet).
- **Properties to Extract:**
  - **Job Title**: The specific name of the role (e.g., "Full Stack Developer").
  - **Contract Type:** Direct from API (e.g., Full-time, Contract, Part-time).
  - **Seniority Level:** Extracted via NLP (e.g., Junior, Senior, Lead, Intern). Used for K-Means clustering.
  - **Job Description**: The source for semantic matching.
  - **Skill Keywords**: Extracted technical competencies from the job posting to enable direct comparison with the curriculum.
  - **Industry Demand Frequency**: How often a skill appears (feeds the Ranking Engine).
  - **Location/Salary**: Contextual metadata for the Philippines market.

---

## **2\. Process Specifications (The Engine & Stack)**

### **A. The Algorithm Pipeline**

The model doesn't just "match" words; it follows a logical sequence to determine "True Gaps."

1. **Vectorization (SBERT \+ GCN):** Converts raw text and the skill ontology graph into "Smart Vectors."
2. **Clustering (K-Means):** Groups jobs into families using Title and Position metadata.
3. **Inference Engine (Reasoning):** Uses a Knowledge Graph to filter out skills logically covered by advanced topics.
4. **Adaptive Ranking (LambdaMART/XGBRanker):** Sorts gaps based on Market Demand and Bloom’s Taxonomy Level.

### **B. The Tech Stack**

- **Frontend (React \+ Tailwind):** Handles file uploads, progress bars for scrapers, and the interactive gap dashboard.
- **Backend (FastAPI):** Orchestrates the ETL pipeline, runs the Python-based ML models, and manages API endpoints.
- **Database (Supabase \+ pgvector):** Stores raw jobs, curriculum metadata, and the mathematical vectors for high-speed similarity searches.

---

## **3\. Output Specifications (The User Dashboard)**

The dashboard must translate complex ML results into actionable academic decisions.

### **A. Information Displayed**

- **Alignment Score:** A percentage representing the overlap between the curriculum and the specific job family.
- **The "True Gap" List:** A prioritized list of missing skills, filtered by the Inference Engine.
- **Skill Badges:**.
  - **Green:** Explicitly found in the syllabus.
  - **Yellow:** Inferred/Logically covered by other topics.
  - **Red:** True Gap (Missing).
- **Cognitive Depth Analysis:** A heatmap visualization showing the curriculum's coverage across **Bloom’s Taxonomy** (e.g., where the curriculum is too focused on "Understanding" vs. "Applying").

### **B. Suggested Actions**

- **Priority Recommendations:** "Adding **Docker** to this course will increase its market alignment by **12%**."
- **Course-to-Job Mapping:** Suggests which specific job roles (e.g., "DevOps Engineer") this curriculum is currently best suited for.

---

## **4\. Developer "Source of Truth" Checklist**

- \[ \] **Stealth Check:** Are the Playwright scrapers using random delays to avoid IP bans?
- \[ \] **Vector Check:** Are we storing SBERT embeddings in the pgvector column in Supabase?
- \[ \] **Inference Check:** Does the model understand that a "React" course doesn't need to be told it also teaches "JavaScript"?
- \[ \] **Ranking Check:** Is the "Missing Skills" list sorted by market frequency, or just alphabetically? (Always use Frequency).
