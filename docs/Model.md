To integrate the **Inference Engine** and **Adaptive Ranking** tiers into the TechGap system, the data requirements expand from simple text matching to a structured dataset that combines industry trends, educational frameworks, and logical relationships.

### **1\. Necessary Model Inputs**

The model now requires a multi-dimensional input set to feed the logical reasoning and ranking layers.

#### **A. Curriculum Data (The "Baseline")**

* **Course/Subject Title:** Used to provide hierarchical context.  
* **Syllabus Text:** The raw content used for keyword extraction and SBERT embedding.  
* **Skill Keywords:** Specific technical competencies already identified in the current MAMOGGA\_Model.ipynb.  
* **Course Level:** (e.g., Introductory, Intermediate, Advanced) to correlate with Bloom's Taxonomy.  
* **Curriculum Specialization**: Identifies the academic track (e.g., CS-IS) to guide the Inference Engine's domain-specific logic

#### **B. Job Market Data (The "Target")**

* **Job Title:** The specific name of the role (e.g., "Full Stack Developer"), used to identify job type.  
* **Seniority Level:** Extracted via NLP from the title and description (e.g., Junior, Senior, Lead). Used as the primary clustering metadata alongside Job Title.  
* **Job Description (Raw Text):** The source for semantic matching and SBERT embedding generation.  
* **Required Skills List:** Extracted keywords from job postings.  
* **Industry Demand Frequency:** How often a specific skill appears across scraped jobs (a key feature for the Ranking Engine).  
* **Salary:** Contextual metadata for the Philippines market (salary\_min, salary\_max).  
* **Source:** Primarily `jobstreet` (Playwright scraper, ongoing background collection). `adzuna` supplements with a one-time burst pull in Week 1 to seed the dataset.  
* **Collection Strategy:** Data collection is **not a blocking step**. The model pipeline begins once 1,500 jobs are available, while the scraper continues running in the background. Target: **5,000 unique job postings** (stretch: 10,000).

#### **C. Knowledge & Framework Data (The "Intelligence")**

* **Skill Ontology (JSON/Graph):** A structured map of relationships (e.g., "Knowledge of *NestJS* implies knowledge of *Node.js* and *TypeScript*").  
* **Bloom’s Taxonomy Metadata:** Classification of skills into cognitive levels (e.g., "Write basic Python" \= Level 1; "Architect a Microservice" \= Level 5).

---

### **2\. Integrated Model Pipeline: Data Flow**

The following flow shows how your previous SBERT/Siamese architecture is now wrapped within the new Inference and Ranking layers.

1. **Input Phase:** Raw Curriculum PDFs and Job Market scrapes are fed into the system.  
2. **Feature Extraction:**  
   * **Text Path:** Uses your existing **SBERT** model to create embeddings for curriculum and job skills.  
   * **Graph Path:** Matches skills against the **Skill Ontology** to find parent/child relationships.  
3. **Inference Engine (Logical Matching):** (family classification happens before the Inference Engine runs, not inside it)  
   * **Input:** SBERT Embeddings \+ Ontology Mappings.  
   * **Process:** The engine checks if a "missing" skill is logically covered by a more advanced skill present in the curriculum (Inference).  
   * **Logic:** If Curriculum\_Skill is a *descendant* of Job\_Skill or vice-versa, the "Gap Score" is adjusted.  
4. **Adaptive Ranking Engine (Prioritization):**  
   * **Input:** "True Gaps" from the Inference Engine \+ Industry Demand Weight \+ Bloom’s Level.  
   * **Process:** Uses a **Learning-to-Rank (LTR)** algorithm (like LambdaMART) to sort the gaps.  
   * **Logic:** A gap in "Basic HTML" (Low Demand, Low Bloom's) is ranked lower than a gap in "System Design" (High Demand, High Bloom's).

---

### **3\. Model Outputs**

The new pipeline moves away from a simple "Match/No-Match" binary and provides a strategic report.

* **Primary Output: The Prioritized Gap List:** A list of skills missing from the curriculum, sorted by a "Necessity Score."  
  * *Example:* 1\. React (High Urgency), 2\. Docker (Medium Urgency), 3\. jQuery (Low Urgency).  
* **Secondary Output: Logical Justifications:** An "Explanation" for why certain skills were *not* flagged as gaps.  
  * *Example:* "JavaScript was not flagged as a gap because 'Advanced React' is present in the curriculum."  
* **Tertiary Output: Cognitive Depth Analysis:** A visualization (like a heat map) showing if the curriculum focuses too much on "Remembering/Understanding" versus industry needs for "Applying/Creating" (Bloom's Taxonomy).

### **Summary of Changes to the Previous Model**

| Component | Status | Modification |
| :---- | :---- | :---- |
| **SBERT Embeddings** | **Keep** | Used as the primary semantic feature. |
| **Siamese Network** | **Modify** | Instead of being the final decision maker, its similarity score becomes just one input for the Inference Engine. |
| **Logistic Regression** | **Repurpose** | Retained as the Job Family Classifier only. Predicts which job cluster a curriculum belongs to (upstream input to the Inference Engine). No longer used for gap detection. |
| **Gap Detection** | **Add** | Added a **filtering step** that uses the Skill Ontology to remove redundant "false gaps." |
| **Data Output** | **Modify** | Changed from an unsorted list of missing keywords to a **Ranked Action Plan**. |

To integrate the **Inference Engine** and **Adaptive Ranking** tiers, your pipeline must evolve from a linear "Compare A to B" model into a multi-layered reasoning system.

### **The New TechGap Model Pipeline**

The updated architecture follows a **Hybrid-Reasoning Pipeline**. It combines deep learning (SBERT/Siamese) with symbolic logic (Knowledge Graphs) and decision optimization (Learning-to-Rank).

#### **Phase 1: Hybrid Feature Extraction (The "Brain" Upgrade)**

Instead of only using SBERT to get text vectors, you will now extract "Structural Context" from an ontology.

* **Algorithms:**  
  * **Sentence-BERT (SBERT):** (Existing) Extracts semantic meaning. Generates 384-dim vectors.  
  * **Node2Vec:** (**Selected**) Processes the Skill Ontology graph (e.g., *React* → *JavaScript*) via random walks + Word2Vec. Generates 64-dim structural vectors. Chosen over GCN because it is unsupervised, requires no training data, and is well-suited for a small (~500-node) skill graph.  
* **The Process:** For every skill in the curriculum and job post, the system generates a **448-dim Hybrid Embedding** (384 SBERT + 64 Node2Vec). This vector contains both semantic meaning and structural position in the tech skill hierarchy.

#### **Phase 2: The Inference Engine (Knowledge-Augmented Matching)**

This replaces the basic "Cosine Similarity" step. It doesn't just ask "Are these words similar?" but "Does knowing X satisfy the requirement for Y?"

* **Algorithms:** \* **Description Logic (DL) Reasoners (e.g., Pellet):** Performs "Subsumption Reasoning" to check if a curriculum skill is a "parent" or "child" of a required job skill.  
  * **Euclidean/Cosine Distance:** Calculated on the *Hybrid Embeddings* from Phase 1\.  
* **The Process:** If a student knows "Redux," the Inference Engine checks the graph, sees it is part of the "React Ecosystem," and avoids flagging a "False Gap" even if the word "React" isn't explicitly in the syllabus.

#### **Phase 3: Adaptive Skill Recommendation Ranking (Priority Layer)**

Once gaps are identified, they are no longer just a "list." They are a prioritized action plan.

* **Algorithms:**  
  * **LambdaMART (via LightGBM) or XGBoost (XGBRanker):** A "Learning-to-Rank" (LTR) algorithm.  
  * **TOPSIS (Multi-Criteria Decision Making):** Used to weight different factors.  
* **The Process:** The model takes all identified gaps and scores them based on:  
  1. **Industry Demand Weight:** How often this skill appears in current web scrapes.  
  2. **Gap Severity:** The mathematical distance between the curriculum and the industry standard.  
  3. **Bloom’s Taxonomy Level:** Priority is given to higher-order gaps (e.g., "Designing Systems" is ranked higher than "Remembering Syntax").

---

### **What Exactly Changes? (Modification Guide)**

To move from your MAMOGGA\_Model.ipynb to this new version, follow this checklist:

| Action | Component | Specific Change |
| :---- | :---- | :---- |
| **ADD** | **Skill Ontology (JSON/RDF)** | Create a custom JSON graph linking related skills (e.g., FastAPI → Python). Run **Node2Vec** on this graph to produce 64-dim structural embeddings per skill. |
| **MODIFY** | **Feature Vector** | Concatenate the 384-dim SBERT/Siamese output with the 64-dim **Node2Vec** embedding AND metadata vectors for Job Seniority Level and Curriculum Track. |
| **ADD** | **Bloom’s Taxonomy Scorer** | Add a Python function (or use an LLM/Keyword classifier) to assign a level (1-6) to every skill in your database. |
| **REPLACE** | **Decision Logic** | Remove the simple LogisticRegression threshold for gaps. Replace it with a **Hybrid Score** ($S \= \\text{Similarity} \+ \\text{Inference Logic Score}$). |
| **REMOVE** | **Flat List Output** | Stop outputting gaps alphabetically or by random order. |
| **ADD** | **Ranking Model** | Train a small XGBRanker model using the identified gaps as items to be sorted based on "Urgency." |
| **MODIFY** | **Data Collection** | JobStreet scraper is the primary source (~150 jobs/day, runs continuously). Adzuna API is a one-time burst supplement for Week 1 seeding and per-track fallback below 300 jobs. Scraper must collect **frequency counts** for each skill to feed the "Industry Demand Weight" for the ranking engine. Pipeline starts at 1,500 jobs; final model uses all collected data (~5,000 target). |

### **Process Flow Summary:**

1. **Input:** Curriculum PDF (with Specialization Tag) \+ Job Post Text (with Title/Position separation).  
2. **Vectorize:** Use **SBERT \+ Node2Vec** to get "Smart Vectors" (448-dim Hybrid Embeddings).  
3. **Reason:** Run the **Inference Engine** to filter out skills that are logically covered by advanced topics.  
4. **Rank:** Run the remaining "True Gaps" through **LambdaMART** to create a prioritized "Action Plan."  
5. **Output:** A ranked dashboard for curriculum developers showing what to fix first.

