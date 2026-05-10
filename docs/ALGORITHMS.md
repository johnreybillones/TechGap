# TechGap — Algorithm & Model Pipeline Documentation

> **Purpose:** This document explains every algorithm used in the TechGap curriculum gap analysis pipeline — why each was chosen, how it works in context, its tradeoffs, and what alternatives were evaluated.

---

## Pipeline Overview

```
PDF Syllabi + Job Postings
        │
        ▼
[1] Skill Extraction (spaCy EntityRuler + en_core_web_md)
        │
        ▼
[2] Hybrid Vectorization (SBERT all-MiniLM-L6-v2 + Node2Vec)
    → 384-dim semantic + 64-dim structural = 448-dim Hybrid Embedding
        │
        ▼
[3] Job Family Clustering (K-Means) + Curriculum Classification (Logistic Regression)
        │
        ▼
[4] Inference Engine (Rule-Based Subsumption on Skill Ontology Graph)
        │
        ▼
[5] Gap Detection (Cosine Similarity on Hybrid Embeddings)
        │
        ▼
[6] Adaptive Ranking (XGBRanker / LambdaMART)
        │
        ▼
[7] Course Anchoring (Cosine Similarity, in-memory numpy)
        │
        ▼
[8] CHED Compliance Guardrails (Deterministic Rule Engine)
        │
        ▼
Dashboard Output (5 Tiers)
```

---

## Phase 1 — Skill Extraction

### Algorithm Used: spaCy EntityRuler + `en_core_web_md`

**What it does:** Extracts named technical skills from job descriptions and syllabus text using a pattern-matching pipeline against a ~500-term Master Skills List. Proper nouns not in the list are flagged as "Candidate Skills" via spaCy's POS tagger.

**Why it was chosen:**
- Fully deterministic — no hallucinations, no API costs
- Extremely fast for 5,000–10,000 job postings
- The skill domain is bounded (~500 IT/CS terms), so a fixed list is sufficient
- Privacy-safe: runs locally, no external API calls

**How it works:**
1. A `Master Skills List` (e.g., Python, Docker, React) is compiled as EntityRuler patterns
2. spaCy matches these patterns against raw text (case-insensitive)
3. Unmatched proper nouns (`en_core_web_md` NER + POS) are surfaced as discovery candidates
4. Frequency counts per skill per track are aggregated → feeds `industry_demand_weight`

**Alternatives Evaluated:**

| Alternative | Verdict |
|---|---|
| **GLiNER (Zero-Shot NER)** | Higher recall for novel skills; better for open-domain. Overkill for a bounded tech skill set. Requires GPU for best performance. |
| **LLM-based extraction (GPT-4o)** | Best contextual accuracy, but high cost per document, latency, and data privacy concerns for academic data. |
| **Hybrid (EntityRuler + GLiNER)** | A future upgrade path: use EntityRuler for high-frequency known skills, GLiNER for unrecognized phrases. |

**Conclusion:** EntityRuler is the right choice for v1 given the bounded domain, zero API cost, and determinism requirements. GLiNER is the recommended upgrade path if the skill list grows beyond 1,000 terms or novel tech stacks become a problem.

---

## Phase 2 — Hybrid Vectorization

### Algorithm A: SBERT (`all-MiniLM-L6-v2`)

**What it does:** Converts course descriptions, CLO text, module activity text, and job descriptions into 384-dimensional dense semantic vectors.

**Why it was chosen:**
- Fine-tuned specifically for semantic similarity (not just token overlap)
- `all-MiniLM-L6-v2` is the lightest viable SBERT model: 22M parameters, ~5× faster than `all-mpnet-base-v2`, sufficient for this use case
- Runs entirely on CPU (no GPU needed), compatible with Supabase Free tier storage constraints
- Natively supported by `sentence-transformers` library; integrates directly with pgvector

**Architecture note:** SBERT *is itself* a Siamese bi-encoder architecture. The `Siamese Network` referenced in legacy model docs (`MAMOGGA_Model.ipynb`) has been **absorbed into SBERT** — there is no need for a separate Siamese layer. SBERT's output embeddings are used directly for cosine similarity.

**Alternatives Evaluated:**

| Model | Dims | Tradeoff |
|---|---|---|
| `all-mpnet-base-v2` | 768 | Better accuracy (+3–5% MTEB), but 5× slower, doubles storage cost in pgvector |
| `e5-small-v2` | 384 | Marginally better MTEB scores than MiniLM; requires instruction prefix ("query:"/"passage:") — adds pipeline complexity |
| `BGE-M3` | 1024 | Production standard for multilingual/hybrid retrieval; overkill for a single-language (English) bounded academic corpus |
| `Qwen3-Embedding-8B` | Large | State-of-the-art accuracy; requires GPU, impractical for this project's infrastructure budget |

**Conclusion:** `all-MiniLM-L6-v2` is the correct choice for this project's constraints (CPU-only, Supabase Free 500MB, 5K–10K documents). If the system scales to 50K+ postings or multilingual curricula, migrate to `bge-base-en-v1.5` or `e5-base-v2`.

---

### Algorithm B: Node2Vec (Graph Structural Embedding)

**What it does:** Processes the Skill Ontology (a ~500-node JSON graph of skill parent-child relationships, e.g., React → JavaScript → Programming) via biased random walks and Skip-Gram (Word2Vec), producing 64-dimensional structural vectors per skill node.

**Why it was chosen:**
- The ontology graph is **small** (~500 nodes, static) — no GPU-based GNNs are needed
- Node2Vec is **unsupervised**: no labeled training data required
- Captures **structural position** in the skill hierarchy: skills that are "siblings" (e.g., React and Vue) get similar structural vectors even if their names are semantically different
- Simple to implement via `node2vec` Python library; integrates cleanly with numpy concatenation

**How it works:**
1. Skill ontology is loaded as a NetworkX graph
2. Node2Vec runs biased random walks (BFS/DFS balance controlled by `p` and `q` hyperparameters)
3. Skip-Gram learns 64-dim embeddings per skill node
4. These embeddings are concatenated with SBERT embeddings: `[384-dim SBERT | 64-dim Node2Vec] = 448-dim Hybrid`

**Alternatives Evaluated:**

| Alternative | Verdict |
|---|---|
| **GCN (Graph Convolutional Network)** | Requires node features + full graph during training. Better for large, feature-rich, dynamic graphs. Overkill for 500-node static ontology. |
| **GraphSAGE** | Inductive learning (handles new nodes without retraining) — valuable for growing ontologies. Recommended upgrade path for v2 if skill list grows dynamically. |
| **TransE / RotatE (KG Embeddings)** | Designed for relational triple learning (head, relation, tail). More suitable for general knowledge graphs with typed relations; adds complexity without significant benefit for a skill hierarchy. |
| **Pure cosine similarity (no graph)** | Ignores structural relationships entirely — cannot distinguish "React (advanced)" from "JavaScript (foundational)" at the graph level. |

**Conclusion:** Node2Vec is optimal for a static, small (~500-node) skill hierarchy with no node features. If the ontology grows to 2,000+ nodes with dynamic additions, GraphSAGE should replace it.

---

## Phase 3 — Job Family Clustering & Classification

### Algorithm A: K-Means Clustering (Job Family Discovery)

**What it does:** Groups the 5,000–10,000 scraped job postings into job "families" (e.g., Web Frontend, DevOps, Data Engineering) using their hybrid embeddings + seniority level metadata.

**Why it was chosen:**
- The project **pre-defines 4 tracks** (CS-IS, CS-GD, IT-WD, IT-NT), so a rough K is known (8–12 job families across 4 tracks is a reasonable upper bound)
- K-Means is fast, interpretable, and its centroids serve as the reference vectors for alignment scoring
- Centroids are directly used in Tier 1 Alignment Score: `cosine_similarity(track_embedding, job_cluster_centroid)`
- Works well in the 448-dim hybrid embedding space for reasonably separated job types

**Alternatives Evaluated:**

| Alternative | Verdict |
|---|---|
| **HDBSCAN** | Better for discovery (no need to pre-specify K), handles noise better, captures arbitrarily-shaped clusters. Downside: does not produce centroids natively, making alignment scoring harder. Recommended if job family boundaries are unclear. |
| **DBSCAN** | Struggles with variable-density clusters (e.g., sparse niche roles vs. dense common roles). Single `epsilon` parameter is hard to tune in 448-dim space. |
| **Gaussian Mixture Models (GMM)** | Soft cluster assignments useful when a job posting spans multiple families. Adds complexity without clear benefit for this use case. |

**Conclusion:** K-Means is justified by the pre-known track structure and the need for centroid-based alignment scoring. If exploratory job family discovery is needed in future iterations, run HDBSCAN first to validate K, then re-run K-Means with that K.

---

### Algorithm B: Logistic Regression (Job Family Classifier)

**What it does:** A supervised multi-class classifier that predicts which job cluster a given curriculum track belongs to, trained on the K-Means cluster labels.

**Why it was chosen:**
- The feature space (448-dim hybrid embeddings) is dense and relatively high-dimensional — Logistic Regression handles this well with L2 regularization
- Only 4 tracks need classification (CS-IS, CS-GD, IT-WD, IT-NT) → very few classes, LR is sufficient
- Fast inference, interpretable coefficients, no hyperparameter complexity
- Proven gold-standard for embedding-space classification

**Alternatives Evaluated:**

| Alternative | Verdict |
|---|---|
| **Linear SVM** | Often matches or beats LR on text embeddings; slightly better margin maximization. Could replace LR if accuracy is insufficient with minimal effort. |
| **Random Forest** | Better at non-linear boundaries, but ensemble trees are slower and less interpretable. Not necessary for 4-class problem. |
| **k-NN Classifier** | Simple, no training phase. Slow at inference on 5K+ embeddings. Not suitable for production API. |
| **Zero-Shot Classification (NLI)** | Could skip clustering entirely. Adds LLM dependency and latency. |

**Conclusion:** Logistic Regression is the correct choice for this 4-class, dense-embedding classification task. Linear SVM is an equally valid alternative and should be benchmarked alongside LR during Week 4 validation.

---

## Phase 4 — Inference Engine (False Gap Elimination)

### Algorithm Used: Rule-Based Subsumption Reasoning on Skill Ontology

**What it does:** Before flagging a skill as a "gap," the engine traverses the Skill Ontology graph to check if the curriculum already teaches a parent or child skill that logically covers the requirement. For example: if a job requires "JavaScript" and the curriculum teaches "React," the engine detects React → JavaScript (parent) and suppresses the false gap.

**Why it was chosen:**
- The skill ontology is a manually curated, trusted source — graph traversal is deterministic and explainable
- No training data needed; pure symbolic reasoning
- Produces the "Logical Justifications" output (e.g., "JavaScript not flagged because Advanced React is present")
- Cheap to implement with NetworkX's ancestor/descendant traversal

**How it works:**
1. For each skill flagged as missing in the curriculum, retrieve its ancestors and descendants from the ontology graph
2. Check if any ancestor or descendant is present in the curriculum's skill set
3. If yes: mark as "Inferred/Covered" (Yellow) — not a true gap
4. If no: mark as "True Gap" (Red) — passes to ranking

**Alternatives Evaluated:**

| Alternative | Verdict |
|---|---|
| **OWL DL Reasoner (Pellet)** | Formally complete subsumption reasoning with consistency checks. Java-based, adds JVM dependency. Overkill for a 500-node Python-native pipeline. |
| **OWL 2 RL (Rule Engine)** | Good for data-heavy ontologies; maps to Datalog. More overhead than plain NetworkX for this scale. |
| **LLM-based inference** | "Does knowing React mean you know JavaScript?" — LLMs answer this correctly but add API latency and cost per inference call. |

**Conclusion:** Rule-based graph traversal (NetworkX) is the right approach for a curated, static, 500-node ontology. The logic is transparent, fast, and explainable — critical for academic stakeholder trust. If the ontology grows beyond 5,000 nodes with complex OWL axioms, migrate to Pellet or OWL 2 RL.

---

## Phase 5 — Gap Detection

### Algorithm Used: Cosine Similarity (on Hybrid Embeddings)

**What it does:** Computes pairwise cosine similarity between curriculum course embeddings and job skill embeddings to determine which skills are semantically present vs. absent.

**Why it was chosen:**
- Standard, well-understood metric for dense embedding spaces
- Magnitude-invariant: focuses on directional similarity regardless of text length
- Directly supported by pgvector (`<=>` operator) for ANN search at scale
- Thresholds (>0.60 MODIFY / 0.40–0.60 ELECTIVE / <0.40 NEW COURSE) are interpretable by domain experts

**Alternatives Evaluated:**

| Alternative | Verdict |
|---|---|
| **BM25 (keyword matching)** | High precision for exact skill names (e.g., "Docker"), but fails on paraphrasing (e.g., "containerization" vs "Docker"). Used as supplementary layer in future hybrid approach. |
| **Cross-Encoder Reranking** | Highest precision for pairwise relevance; but O(n²) cost — cannot precompute. Too slow for 5K jobs × N courses. Reserve for top-K reranking in v2. |
| **Euclidean Distance** | Less robust than cosine in high-dimensional spaces (curse of dimensionality); not magnitude-invariant. |
| **Dot Product** | Equivalent to cosine similarity only when vectors are normalized. pgvector supports both. |

**Conclusion:** Cosine similarity via pgvector is the correct choice for scalable, precomputed similarity search. The hybrid BM25 + cosine approach is the recommended upgrade path if exact-keyword precision becomes a requirement.

---

## Phase 6 — Adaptive Ranking (Learning to Rank)

### Algorithm Used: XGBRanker (LambdaMART via XGBoost)

**What it does:** Sorts the "True Gap" skill list into a priority-ordered action plan using three signals: Industry Demand Weight, Gap Severity (cosine distance), and Bloom's Taxonomy Level.

**Why it was chosen:**
- LambdaMART directly optimizes listwise ranking metrics (NDCG) — not just binary classification
- XGBoost is production-ready, CPU-efficient, and well-supported in Python
- The three ranking signals (demand, severity, bloom level) are exactly the multi-feature input format LambdaMART is designed for
- No labeled ranking training data needed for initial version: synthetic relevance labels can be derived from the formula: `urgency = demand_weight × gap_severity × bloom_level_normalized`

**How it works:**
1. Each True Gap becomes a ranked item with features: `[industry_demand_weight, gap_severity_score, bloom_level, course_type_flexibility]`
2. XGBRanker trained with `objective="rank:ndcg"` using synthetic relevance labels
3. Output: sorted gap list by urgency score (0.0–1.0)

**Note on TOPSIS:** The docs mention TOPSIS as a multi-criteria decision method for weighting ranking factors. TOPSIS is a valid alternative for computing the composite urgency score without training a model — it ranks alternatives by distance to an ideal solution. **For v1, TOPSIS can serve as the scoring formula if no training data exists**, with XGBRanker replacing it once curriculum experts provide labeled gap priority data.

**Alternatives Evaluated:**

| Alternative | Verdict |
|---|---|
| **LambdaMART via LightGBM** | Equivalent algorithm, slightly faster training. Either XGBoost or LightGBM is valid. |
| **TOPSIS** | Deterministic MCDM, no training data needed. Good for v1 baseline scoring formula. Lacks the adaptive learning capability of LambdaMART. |
| **Simple Weighted Sum** | `urgency = w1×demand + w2×severity + w3×bloom`. Simplest possible approach. Lacks interaction effects between features. Good sanity check baseline. |
| **Neural Ranker (BERT-based)** | Best for complex semantic ranking. Overkill for 3-feature input; impractical without large labeled datasets. |

**Conclusion:** XGBRanker is the right production algorithm. **Recommendation:** implement TOPSIS first as a deterministic baseline (no training data needed), then replace with XGBRanker once 50+ curriculum expert-labeled gap priority examples are available.

---

## Phase 7 — Course Anchoring

### Algorithm Used: Cosine Similarity (in-memory numpy)

**What it does:** For each ranked gap skill, computes cosine similarity against all curriculum course embeddings to find the best "anchor course" for the gap (MODIFY / ELECTIVE / NEW COURSE decision).

**Why it was chosen:**
- Curriculum data is small (typically 30–80 courses per track) — in-memory numpy is faster than a pgvector round-trip
- Same metric as gap detection ensures consistency in threshold interpretation
- `argmax(cosine_sim(gap_embedding, course_embeddings))` is a single numpy operation — O(n) per gap

**Thresholds:**
- `> 0.60` → MODIFY existing course
- `0.40–0.60` → Suggest new ELECTIVE
- `< 0.40` → Recommend NEW COURSE

These thresholds are **empirically derived defaults** and should be calibrated against domain expert labeling during Week 4 validation.

---

## Phase 8 — CHED Compliance Guardrails

### Algorithm Used: Deterministic Rule Engine (Python if/else)

**What it does:** Applies 6 hard constraints derived from CHED CMO No. 25, Series of 2015 to every suggestion before it reaches the dashboard.

**Why it was chosen:**
- Regulatory compliance must be 100% deterministic — no ML model should have any authority over compliance decisions
- Rules are clearly defined (146-unit floor, CC101–CC106 protection, etc.)
- Zero risk of "approximate" compliance from a probabilistic model

**Rules:**
1. Protected courses (CC101–CC106): action forced to ENHANCE-only (no removal)
2. 146-unit floor: new course suggestions validated against `SUM(units)` from curriculum
3. Flexibility hierarchy: elective > professional > core > GE for anchoring preference
4. Program outcome mapping: every suggestion must map to ≥1 CHED outcome (CS01–CS10 / IT01–IT10)
5. Thesis vs. Capstone: `program_type` determines job family and Bloom's prioritization
6. Faculty qualification warnings: emitted when suggested skill category has no existing faculty coverage

---

## Bloom's Taxonomy Scorer

### Algorithm Used: Keyword Classifier (Verb Extraction from CLOs)

**What it does:** Assigns a Bloom's cognitive level (L1–L6) to each skill by extracting action verbs from Course Learning Outcomes (CLOs) and mapping them to Bloom's taxonomy verbs.

**Why it was chosen:**
- CLOs in Philippine syllabi follow OBE format with explicit Bloom's verbs (e.g., "Analyze," "Create," "Apply")
- A verb-to-level lookup table is deterministic and requires no training data
- Results are stored per course and aggregated into the Bloom's distribution heatmap

**Example mapping:**
- *Remember, Identify, List* → L1
- *Explain, Describe, Understand* → L2
- *Apply, Use, Execute* → L3
- *Analyze, Compare, Differentiate* → L4
- *Evaluate, Justify, Critique* → L5
- *Create, Design, Construct* → L6

**Alternatives Evaluated:**
- **LLM-based Bloom's classification:** Higher accuracy for ambiguous verbs, but adds API cost and non-determinism. Viable upgrade if verb extraction alone is insufficient.
- **Fine-tuned classifier (BERT + Bloom's labels):** Requires labeled training data. Not justified for v1.

---

## Seniority Level Extraction

### Algorithm Used: spaCy Pattern Matching (Rule-Based)

**What it does:** Extracts seniority signals (Junior, Mid-level, Senior, Lead, Intern) from job titles and descriptions via regex/token pattern matching.

**Why it was chosen:**
- Seniority signals in job postings are highly formulaic ("Senior Software Engineer," "Junior Developer")
- Used as K-Means clustering metadata — exact token matching is sufficient
- Zero latency, no model overhead

---

## Summary: Algorithm Decisions Matrix

| Pipeline Phase | Algorithm Used | Status | Upgrade Path |
|---|---|---|---|
| Skill Extraction | spaCy EntityRuler + `en_core_web_md` | ✅ Optimal for v1 | GLiNER for open-domain skills |
| Semantic Embedding | SBERT `all-MiniLM-L6-v2` | ✅ Optimal for CPU/free-tier | `bge-base-en-v1.5` at scale |
| Graph Embedding | Node2Vec (64-dim) | ✅ Optimal for static 500-node graph | GraphSAGE for dynamic ontology |
| Job Clustering | K-Means | ✅ Justified by known track structure | HDBSCAN for discovery phase |
| Curriculum Classifier | Logistic Regression | ✅ Correct for 4-class embedding task | Linear SVM as benchmark |
| Inference Engine | Rule-Based Graph Traversal | ✅ Deterministic, explainable | OWL DL Reasoner at 5K+ nodes |
| Gap Detection | Cosine Similarity (pgvector) | ✅ Scalable, precomputable | + BM25 hybrid for keyword precision |
| Gap Ranking | XGBRanker (LambdaMART) | ⚠️ Use TOPSIS for v1 baseline | XGBRanker with expert-labeled data |
| Course Anchoring | Cosine Similarity (numpy) | ✅ Correct for small in-memory set | No change needed |
| Bloom's Scoring | Verb Keyword Classifier | ✅ Optimal for OBE CLO format | LLM for ambiguous cases |
| CHED Compliance | Deterministic Rule Engine | ✅ Non-negotiable | No ML — always deterministic |

---

## Key Architectural Decisions & Rationale

### Why Hybrid Embeddings (SBERT + Node2Vec)?

Pure SBERT embeddings cannot distinguish structural relationships. The word "React" and "Vue.js" have similar semantic embeddings (both are frontend frameworks), but their *position in the skill hierarchy* differs. Node2Vec encodes this structural position — React sits deeper in the JavaScript ecosystem than Vue.js in some ontology configurations. The 448-dim hybrid captures both the *meaning* and the *position* of a skill, producing more accurate gap detection than either alone.

### Why Not Use an LLM End-to-End?

The system was deliberately designed to be **LLM-free in inference**. Every output tier is computed deterministically (cosine similarity, rule-based guardrails, SQL aggregation). This ensures:
1. **Reproducibility** — same inputs always produce same outputs
2. **Cost** — no per-call API costs for potentially thousands of pipeline runs
3. **Explainability** — every recommendation has a traceable mathematical justification
4. **CHED Trust** — academic institutions require auditable, not probabilistic, compliance decisions

### Why pgvector (not Pinecone/Weaviate)?

Supabase Free tier (500MB) is sufficient for 5K–10K job embeddings at 384 dimensions (≈7MB for 5K × 384 × 4 bytes). pgvector collocates embeddings with metadata (job title, track, seniority) enabling SQL JOIN operations that external vector databases cannot perform. HNSW indexing in pgvector provides sub-millisecond ANN search at this scale.

### The Siamese Network Clarification

The legacy `MAMOGGA_Model.ipynb` used a separate Siamese network architecture layered on top of raw BERT embeddings. This is now **superseded**. SBERT (`sentence-transformers`) already implements the Siamese bi-encoder architecture internally — it is what makes SBERT produce semantically comparable sentence embeddings in the first place. Adding another Siamese layer on top of SBERT embeddings is redundant. The correct usage is: encode with SBERT → compare with cosine similarity. The Siamese concept is preserved within SBERT itself.

---

## References

- Reimers & Gurevych (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.* EMNLP 2019.
- Grover & Leskovec (2016). *node2vec: Scalable Feature Learning for Networks.* KDD 2016.
- Burges et al. (2010). *From RankNet to LambdaRank to LambdaMART: An Overview.* Microsoft Research.
- Hwang & Yoon (1981). *Multiple Attribute Decision Making: Methods and Applications (TOPSIS).*
- CHED CMO No. 25, Series of 2015. *Policies, Standards and Guidelines for BSCS/BSIT Programs.*
- MTEB Leaderboard (2026). *Massive Text Embedding Benchmark.* HuggingFace.
