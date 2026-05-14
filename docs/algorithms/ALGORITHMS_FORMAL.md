# TechGap — Formal Algorithm Specifications

> **Note:** Only algorithms that have all four components — implication, pseudocode, mathematical formula, and time complexity — are included. Algorithms such as the spaCy EntityRuler (rule-based, no formal formula) and the CHED Compliance Rule Engine (deterministic if/else, no formula) are documented in `ALGORITHMS.md` but excluded here.

---

## 3.4.1 Sentence-BERT (SBERT)

Sentence-BERT (SBERT) is a transformer-based deep learning model built specifically to generate fixed-length, semantically meaningful representations of text. Unlike conventional BERT, which produces token-level contextual outputs, SBERT employs a Siamese bi-encoder architecture internally, passing each text through the same shared network to produce sentence-level embeddings that are directly comparable via cosine similarity. In TechGap, SBERT (`all-MiniLM-L6-v2`) serves as the primary semantic feature extractor, converting raw curriculum course descriptions, Course Learning Outcomes (CLOs), module activity text, and job posting descriptions into 384-dimensional dense vectors. These embeddings form the semantic component of the 448-dimensional Hybrid Embedding used across all downstream pipeline phases, enabling the system to measure the semantic closeness between academic content and industry requirements without relying on exact keyword overlap.

### 3.4.1.1 Implication of SBERT in the System

Sentence-BERT (SBERT) is the primary semantic embedding backbone of TechGap. It converts raw text — course descriptions, Course Learning Outcomes (CLOs), module activity text, and job posting descriptions — into fixed-length, 384-dimensional dense vectors that capture semantic meaning beyond keyword overlap.

In the TechGap pipeline, SBERT (`all-MiniLM-L6-v2`) is used to:
- Embed all job posting descriptions into `jobs_raw.description_embedding` (stored in Supabase via pgvector)
- Embed curriculum course descriptions and CLO text in-memory at pipeline runtime (not stored in Supabase)
- Produce the 384-dimensional semantic component of the 448-dimensional Hybrid Embedding

SBERT uses a Siamese bi-encoder architecture internally: both sentences in a pair are passed through the same BERT-based network independently, enabling precomputed embeddings and fast cosine similarity comparisons. This is why a separate Siamese Network layer is not needed — SBERT already implements it.

### 3.4.1.2 Pseudocode

```
1.  Initialize pretrained SBERT model (all-MiniLM-L6-v2, 384-dim output)
2.  For each text document T in dataset do
3.      Clean T: remove HTML tags, normalize whitespace, truncate to 256 tokens
4.      Tokenize T into token sequence [t1, t2, ..., tL]
5.      Pass token sequence through 6-layer MiniLM transformer encoder
6.          Compute attention scores: A = softmax(QK^T / sqrt(d_k)) * V
7.          Propagate through all L encoder layers
8.      Apply mean pooling over all token embeddings h1..hL:
9.          E = (1/L) * sum(h_i) for i in 1..L
10.     Normalize embedding: E_norm = E / ||E||_2
11.     Store E_norm as the document embedding
12. End For
13. Return all document embeddings
```

*Figure 3.4.1.2 Pseudocode of SBERT Algorithm*

The SBERT algorithm encodes raw text documents into fixed-length, semantically comparable vectors. The pretrained `all-MiniLM-L6-v2` model is first initialized. For each text document in the dataset — whether a job description or a curriculum course description — the text is cleaned by stripping HTML tags and normalizing whitespace before being truncated to fit within the model's 256-token limit. The cleaned text is then tokenized and passed through SBERT's six-layer MiniLM transformer encoder, where self-attention mechanisms compute contextual relationships across all tokens simultaneously. Mean pooling is applied across all token-level hidden states to produce a single, fixed-length 384-dimensional vector that represents the whole document. This pooled vector is then L2-normalized so that all embeddings share a consistent magnitude, making downstream cosine similarity comparisons valid and scale-independent. The process repeats for every document in the dataset, and the complete collection of normalized embeddings is returned for use in clustering, gap detection, and course anchoring.

### 3.4.1.3 Formula and Mathematical Computations

**Self-Attention Mechanism (per transformer layer):**

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

where Q, K, V are the query, key, and value matrices; d_k is the key dimension.

**Mean Pooling over Token Embeddings:**

$$\mathbf{E} = \frac{1}{L} \sum_{i=1}^{L} \mathbf{h}_i$$

where h_i is the hidden state of the i-th token and L is the sequence length.

**L2 Normalization:**

$$\hat{\mathbf{E}} = \frac{\mathbf{E}}{||\mathbf{E}||_2}$$

**Cosine Similarity (used downstream for gap detection and course anchoring):**

$$\text{cos\_sim}(\mathbf{A}, \mathbf{B}) = \frac{\mathbf{A} \cdot \mathbf{B}}{||\mathbf{A}|| \cdot ||\mathbf{B}||}= \frac{\sum_{i=1}^{d} a_i b_i}{\sqrt{\sum_{i=1}^{d} a_i^2} \cdot \sqrt{\sum_{i=1}^{d} b_i^2}}$$

### 3.4.1.4 Time Complexity

| Operation | Complexity |
|---|---|
| Tokenization per document | O(L) |
| Self-attention per layer | O(L² × d_k) |
| Full encoder (6 layers) | O(6 × L² × d_k) |
| Mean pooling | O(L × d) |
| L2 normalization | O(d) |
| **Full pipeline for N documents** | **O(N × L² × d_k)** |

where N = number of documents, L = sequence length (max 256 tokens), d_k = key dimension (64 for MiniLM). For 10,000 job postings at L=256, this is approximately 40M operations — feasible on CPU in under 30 minutes.

---

## 3.4.2 Node2Vec

Node2Vec is an unsupervised graph embedding algorithm that learns low-dimensional vector representations of nodes in a graph by simulating biased random walks and training a Skip-Gram model on the resulting walk sequences. In TechGap, Node2Vec processes the Skill Ontology — a directed graph of approximately 500 nodes representing skill parent-child relationships (e.g., React → JavaScript → Programming) — to produce 64-dimensional structural embeddings for each skill node. These structural vectors encode each skill's position within the technology hierarchy, allowing the system to distinguish between skills that may be semantically similar in text but occupy different structural roles in the skill graph. The 64-dimensional Node2Vec output is concatenated with the 384-dimensional SBERT output to form the 448-dimensional Hybrid Embedding, which is the core feature vector used across all downstream pipeline phases including clustering, gap detection, and course anchoring.

### 3.4.2.1 Implication of Node2Vec in the System

Node2Vec generates the 64-dimensional structural component of TechGap's 448-dimensional Hybrid Embedding. It processes the Skill Ontology — a directed graph of approximately 500 nodes representing skill parent-child relationships (e.g., React → JavaScript → Programming) — and produces an embedding for each skill node that encodes its structural position in the tech skill hierarchy.

These structural embeddings allow the system to distinguish between skills that may be semantically similar (e.g., "React" and "Vue.js" both relate to frontend) but occupy different positions in the skill hierarchy. The 64-dim Node2Vec output is concatenated with the 384-dim SBERT output to form the final 448-dim Hybrid Embedding used across all downstream phases.

### 3.4.2.2 Pseudocode

```
1.  Load Skill Ontology as directed graph G = (V, E)
    where V = set of ~500 skill nodes, E = parent-child edges
2.  Set hyperparameters: walk_length l, num_walks r, p (return), q (in-out)
3.  For each node v in V do
4.      For walk w = 1 to r do
5.          Initialize walk W = [v]
6.          While |W| < l do
7.              curr = last node in W
8.              prev = second-to-last node in W (if exists)
9.              Compute transition probabilities for each neighbor x of curr:
10.                 If x == prev:       weight = 1/p
11.                 Else if d(prev,x) == 1: weight = 1.0
12.                 Else:               weight = 1/q
13.             Normalize weights; sample next node x using these weights
14.             Append x to W
15.         End While
16.         Store walk W
17.     End For
18. End For
19. Train Skip-Gram model on all collected walks:
20.     For each walk W do
21.         For each node v in W do
22.             Maximize: log P(N(v) | f(v))
23.             where N(v) = neighborhood nodes within context window k
24.         End For
25.     End For
26. Return 64-dim embedding vector f(v) for each node v in V
```

*Figure 3.4.2.2 Pseudocode of Node2Vec Algorithm*

The Node2Vec algorithm derives structural embeddings for each node in the Skill Ontology graph. The ontology is first loaded as a directed NetworkX graph whose nodes represent individual skills and whose edges represent parent-child skill relationships. Hyperparameters controlling walk behavior — including walk length, number of walks per node, and the return (`p`) and in-out (`q`) bias parameters — are then set. For every node in the graph, a specified number of random walks is generated: each walk starts at the current node and grows step-by-step by sampling the next node from among the current node's neighbors according to biased transition probabilities derived from `p` and `q`. A small `p` encourages the walk to return to previously visited nodes (BFS-like, capturing local structure), while a small `q` encourages the walk to move outward to new neighborhoods (DFS-like, capturing global structure). Once all walks across all nodes have been generated, a Skip-Gram model is trained on the collected walk sequences, learning to predict which nodes tend to co-appear in the same walk context window. The result is a 64-dimensional embedding vector for every skill node in the ontology, capturing its structural role and relationships within the technology hierarchy.

### 3.4.2.3 Formula and Mathematical Computations

**Biased Transition Probability:**

$$\pi(v, x) = \frac{1}{Z} \cdot \alpha_{pq}(t, x) \cdot w(v, x)$$

where Z is a normalizing constant, w(v,x) is the edge weight, and:

$$\alpha_{pq}(t, x) = \begin{cases} \frac{1}{p} & \text{if } d_{tx} = 0 \\ 1 & \text{if } d_{tx} = 1 \\ \frac{1}{q} & \text{if } d_{tx} = 2 \end{cases}$$

where t is the previous node and d_tx is the shortest path distance between t and x.

**Skip-Gram Objective (maximized during training):**

$$\max_{f} \sum_{v \in V} \left[ -\log Z_v + \sum_{n_i \in N(v)} f(n_i) \cdot f(v) \right]$$

**Negative Sampling Approximation:**

$$\log \sigma(f(n_i) \cdot f(v)) + \sum_{k=1}^{K} \mathbb{E}_{v_k \sim P_n} [\log \sigma(-f(v_k) \cdot f(v))]$$

**Hybrid Embedding Concatenation:**

$$\mathbf{H}_{skill} = [\hat{\mathbf{E}}_{SBERT} \| \mathbf{f}_{Node2Vec}] \in \mathbb{R}^{384+64} = \mathbb{R}^{448}$$

### 3.4.2.4 Time Complexity

| Operation | Complexity |
|---|---|
| Random walk generation | O(\|V\| × r × l) |
| Skip-Gram training | O(\|V\| × r × l × k) |
| **Total Node2Vec** | **O(\|V\| × r × l × k)** |

where |V| = 500 nodes, r = number of walks per node (default 10), l = walk length (default 80), k = context window size (default 5). For the 500-node ontology, this is approximately 2M operations — completes in seconds on CPU.

---

## 3.4.3 K-Means Clustering

K-Means is an unsupervised machine learning algorithm that partitions a dataset into a predefined number of clusters by iteratively minimizing the within-cluster sum of squared distances between data points and their assigned cluster centroid. In TechGap, K-Means operates on the 448-dimensional Hybrid Embeddings of 5,000 to 10,000 scraped job postings, augmented with seniority level metadata, to automatically discover job "families" such as Web Frontend, DevOps, or Data Engineering. The number of clusters K is set between 8 and 12, guided by the four pre-defined curriculum specialization tracks (CS-IS, CS-GD, IT-WD, IT-NT). K-Means++ seeding is used to initialize centroids intelligently, reducing the risk of poor convergence. The resulting cluster centroids serve a dual role in the system: they act as industry reference vectors for computing the Tier 1 Alignment Score per curriculum track, and their associated cluster labels become the training targets for the downstream Logistic Regression job family classifier.

### 3.4.3.1 Implication of K-Means in the System

K-Means groups the 5,000–10,000 scraped job postings into job "families" (e.g., Web Frontend, DevOps, Network Engineering) using their 448-dimensional Hybrid Embeddings augmented with seniority level metadata. These clusters define the industry reference groups against which each curriculum track is compared.

The cluster centroids produced by K-Means serve a dual purpose: (1) as the reference vectors for computing the Tier 1 Alignment Score (cosine similarity between a curriculum track's embedding and its matched cluster centroid), and (2) as training labels for the downstream Logistic Regression job family classifier.

### 3.4.3.2 Pseudocode

```
1.  Input: N job embeddings X = {x1, x2, ..., xN} in R^448
2.  Input: K = number of job families (determined by track structure, ~8-12)
3.  Initialize K centroids mu_1..mu_K using K-Means++ seeding:
4.      Select first centroid mu_1 uniformly at random from X
5.      For k = 2 to K do
6.          Compute D(x) = min distance from x to nearest existing centroid
7.          Select next centroid with probability proportional to D(x)^2
8.      End For
9.  Repeat until convergence:
10.     Assignment step:
11.         For each job embedding x_i do
12.             c_i = argmin_k ||x_i - mu_k||^2
13.         End For
14.     Update step:
15.         For each cluster k = 1 to K do
16.             mu_k = (1 / |C_k|) * sum(x_i) for all x_i in C_k
17.         End For
18.     Check convergence: if centroids unchanged, stop
19. End Repeat
20. Return cluster assignments C = {c_1..c_N} and centroids {mu_1..mu_K}
```

*Figure 3.4.3.2 Pseudocode of K-Means Clustering Algorithm*

The K-Means clustering algorithm groups job posting embeddings into semantically coherent job families. The process begins by accepting the full set of job Hybrid Embeddings and the target number of clusters K. Centroids are initialized using K-Means++ seeding: the first centroid is chosen uniformly at random from the embeddings, and each subsequent centroid is selected with probability proportional to the squared distance from the nearest already-chosen centroid, ensuring initial centroids are well spread across the embedding space. The algorithm then enters an iterative loop. In the assignment step, every job embedding is assigned to the cluster whose centroid is closest to it in Euclidean distance. In the update step, each centroid is recomputed as the arithmetic mean of all embeddings currently assigned to that cluster. These two steps repeat until the centroid positions no longer change between iterations, indicating convergence. Upon convergence, the algorithm returns the cluster assignment for every job posting and the final set of cluster centroids. These centroids become the industry reference points used throughout the rest of the TechGap pipeline.

### 3.4.3.3 Formula and Mathematical Computations

**Cluster Assignment:**

$$c_i = \arg\min_{k \in \{1,\ldots,K\}} ||\mathbf{x}_i - \boldsymbol{\mu}_k||^2$$

**Centroid Update:**

$$\boldsymbol{\mu}_k = \frac{1}{|C_k|} \sum_{\mathbf{x}_i \in C_k} \mathbf{x}_i$$

**Objective Function (Within-Cluster Sum of Squares, minimized):**

$$J = \sum_{k=1}^{K} \sum_{\mathbf{x}_i \in C_k} ||\mathbf{x}_i - \boldsymbol{\mu}_k||^2$$

**Alignment Score (Tier 1, post-clustering):**

$$\text{AlignmentScore}(\text{track}) = \cos(\mathbf{H}_{track},\ \boldsymbol{\mu}_{k^*}) \times 100\%$$

where k* is the cluster matched to the curriculum track via Logistic Regression.

### 3.4.3.4 Time Complexity

| Operation | Complexity |
|---|---|
| K-Means++ initialization | O(K × N × d) |
| Assignment step (per iteration) | O(N × K × d) |
| Update step (per iteration) | O(N × d) |
| **Full K-Means (T iterations)** | **O(T × N × K × d)** |

where N = 10,000 jobs, K = 12 clusters, d = 448 dimensions, T = iterations (typically 20–100). This is approximately 540M operations per iteration — completes in under 60 seconds on CPU using scikit-learn's optimized implementation.

---

## 3.4.4 Logistic Regression (Job Family Classifier)

Logistic Regression is a supervised multi-class classification algorithm that models the probability of a data point belonging to each of several predefined classes by applying a softmax transformation over a set of learned linear decision boundaries. In TechGap, Logistic Regression serves as the Job Family Classifier: it is trained on the cluster labels produced by K-Means and learns to predict which job cluster a given curriculum track's 448-dimensional Hybrid Embedding belongs to. This classification step is critical because it determines which job family centroid is used as the industry reference vector when computing the Tier 1 Alignment Score — ensuring that a CS-IS curriculum is compared against Data Engineering job roles rather than Web Development roles, for example. L2 regularization is applied during training to prevent overfitting on the relatively small number of labeled training samples derived from K-Means assignments. At inference time, the classifier takes a curriculum track's hybrid embedding as input and outputs a probability distribution over all K job family classes, with the highest-probability class selected as the matched job family.

### 3.4.4.1 Implication of Logistic Regression in the System

Logistic Regression serves as the Job Family Classifier in TechGap. It is trained on the K-Means cluster labels (Phase 3A) and predicts which job cluster a given curriculum track's hybrid embedding belongs to. This step is critical because it determines which job family's centroid is used as the industry reference for gap detection — comparing a CS-IS curriculum against Data Engineering jobs rather than Web Development jobs, for example.

The classifier takes a 448-dim Hybrid Embedding as input and outputs a probability distribution over the K job family classes. The argmax class is the matched job family. L2 regularization prevents overfitting on the relatively small number of curriculum tracks.

### 3.4.4.2 Pseudocode

```
1.  Input: Labeled training set {(x_i, y_i)} where x_i in R^448, y_i in {1..K}
    Labels y_i come from K-Means cluster assignments
2.  Initialize weight matrix W in R^(K x 448) and bias b in R^K
3.  Training loop (for T epochs):
4.      For each batch B of (x_i, y_i) pairs do
5.          Compute logits: z = W * x_i + b
6.          Compute softmax probabilities:
7.              P(y=k | x_i) = exp(z_k) / sum_j(exp(z_j))  for k = 1..K
8.          Compute cross-entropy loss with L2 regularization:
9.              L = -sum_k(y_k * log P(y=k|x)) + lambda * ||W||_F^2
10.         Compute gradients: dL/dW, dL/db
11.         Update: W = W - lr * dL/dW
12.                 b = b - lr * dL/db
13.     End For
14. End Loop
15. Inference:
16.     Given curriculum embedding x_curr:
17.     z = W * x_curr + b
18.     predicted_family = argmax_k softmax(z)
19. Return predicted_family and probability distribution
```

*Figure 3.4.4.2 Pseudocode of Logistic Regression Algorithm*

The Logistic Regression training procedure learns to classify curriculum track embeddings into job family clusters. The process begins by accepting the full set of labeled training samples, where each sample is a 448-dimensional Hybrid Embedding paired with a K-Means cluster label as its target class. A weight matrix and bias vector are initialized to map the input embedding space to K output classes. Training proceeds in batches over multiple epochs: for each batch, logits are computed as the linear combination of the weight matrix and the input embedding, and softmax is applied to convert these logits into class probabilities. The cross-entropy loss between the predicted probabilities and the true K-Means labels is computed, augmented by an L2 regularization penalty on the weight matrix to discourage overfitting. Gradients of the total loss with respect to the weights and bias are computed, and the parameters are updated by gradient descent. Once training converges, the classifier is used at inference time: given a curriculum track's hybrid embedding, the model computes logits, applies softmax, and selects the class with the highest predicted probability as the matched job family.

### 3.4.4.3 Formula and Mathematical Computations

**Softmax Activation (multi-class probability):**

$$P(y = k \mid \mathbf{x}) = \frac{e^{\mathbf{w}_k \cdot \mathbf{x} + b_k}}{\sum_{j=1}^{K} e^{\mathbf{w}_j \cdot \mathbf{x} + b_j}}$$

**Cross-Entropy Loss:**

$$\mathcal{L}_{CE} = -\sum_{k=1}^{K} y_k \log P(y = k \mid \mathbf{x})$$

**L2-Regularized Objective (minimized during training):**

$$\mathcal{L}_{total} = \mathcal{L}_{CE} + \lambda ||\mathbf{W}||_F^2 = -\sum_{k=1}^{K} y_k \log P(y=k|\mathbf{x}) + \lambda \sum_{k,d} w_{kd}^2$$

**Prediction:**

$$\hat{y} = \arg\max_{k \in \{1,\ldots,K\}} P(y = k \mid \mathbf{x})$$

### 3.4.4.4 Time Complexity

| Operation | Complexity |
|---|---|
| Forward pass (logits) | O(K × d) |
| Softmax computation | O(K) |
| Gradient computation | O(K × d) |
| **Training (T epochs, N samples)** | **O(T × N × K × d)** |
| **Inference (single embedding)** | **O(K × d)** |

where K = 12 job families, d = 448, N = number of curriculum tracks (small, ~20–50). Training completes in milliseconds. Inference is effectively instantaneous.

---

## 3.4.5 Cosine Similarity

Cosine similarity is a metric that measures the directional agreement between two vectors in a high-dimensional space by computing the cosine of the angle between them, independently of their magnitudes. Because it is magnitude-invariant, cosine similarity is the standard matching metric for normalized dense embedding spaces. In TechGap, cosine similarity is applied at two distinct stages of the pipeline. In Phase 5 (Gap Detection), it measures pairwise semantic similarity between curriculum course embeddings and job skill embeddings stored in Supabase via pgvector, using the `<=>` cosine distance operator for scalable approximate nearest-neighbor search. In Phase 7 (Course Anchoring), it is computed in-memory using numpy to find which existing curriculum course is most semantically aligned with each ranked gap skill, and the resulting similarity score determines the recommended action type: a score above 0.60 triggers a MODIFY recommendation, a score between 0.40 and 0.60 triggers an ELECTIVE recommendation, and a score below 0.40 triggers a NEW COURSE recommendation.

### 3.4.5.1 Implication of Cosine Similarity in the System

Cosine Similarity is the core matching metric used in two distinct phases of TechGap: **Gap Detection** (Phase 5) and **Course Anchoring** (Phase 7). It measures the directional agreement between two embedding vectors, regardless of their magnitude, making it ideal for comparing normalized SBERT/Hybrid embeddings in a high-dimensional semantic space.

In Gap Detection, cosine similarity computes the match between each curriculum course embedding and each job skill embedding stored in Supabase via pgvector (using the `<=>` cosine distance operator). In Course Anchoring, it is computed in-memory using numpy to find which existing course best absorbs a ranked gap skill, and the resulting score determines the action type (MODIFY / ELECTIVE / NEW COURSE).

### 3.4.5.2 Pseudocode

```
1.  Input: Gap skill embedding g in R^448
2.  Input: Set of curriculum course embeddings C = {c_1..c_M} in R^448
3.  Input: Similarity thresholds: T_high = 0.60, T_low = 0.40
4.  For each gap skill g in ranked True Gap list do
5.      sim_scores = []
6.      For each course embedding c_j in C do
7.          dot  = sum(g_i * c_j_i) for i in 1..448
8.          norm_g = sqrt(sum(g_i^2))
9.          norm_c = sqrt(sum(c_j_i^2))
10.         sim = dot / (norm_g * norm_c)
11.         sim_scores.append((sim, j))
12.     End For
13.     Sort sim_scores descending
14.     best_sim, best_course = sim_scores[0]
15.     If best_sim > T_high:
16.         action = "MODIFY"
17.     Else if best_sim >= T_low:
18.         action = "ELECTIVE"
19.     Else:
20.         action = "NEW COURSE"
21.     Record: anchor_course = best_course, similarity = best_sim, action = action
22.     Also record 2nd and 3rd highest for alternative_courses output
23. End For
24. Return anchoring decisions for all gap skills
```

*Figure 3.4.5.2 Pseudocode of Cosine Similarity Algorithm*

The cosine similarity algorithm determines the best curriculum course anchor for each identified gap skill and decides what type of curricular action is required. For each gap skill in the ranked list, the algorithm iterates over every curriculum course embedding in the current track. For each course, the dot product between the gap skill embedding and the course embedding is computed, and both vectors' L2 norms are calculated. The cosine similarity score is then derived by dividing the dot product by the product of the two norms, yielding a value between -1 and 1. All similarity scores across courses are collected and sorted in descending order. The course with the highest similarity score is selected as the anchor course. The similarity value is then compared against two thresholds: if it exceeds 0.60, the action is classified as MODIFY, indicating the gap skill can be integrated into the existing course; if it falls between 0.40 and 0.60, the action is ELECTIVE, suggesting a new elective course should be offered; if it falls below 0.40, the action is NEW COURSE, indicating the gap requires an entirely new foundational course. The second and third highest-scoring courses are also recorded as alternative anchors. This process repeats for every gap skill in the ranked list, and the full set of anchoring decisions is returned for dashboard presentation.

### 3.4.5.3 Formula and Mathematical Computations

**Cosine Similarity:**

$$\text{sim}(\mathbf{A}, \mathbf{B}) = \frac{\mathbf{A} \cdot \mathbf{B}}{||\mathbf{A}|| \cdot ||\mathbf{B}||} = \frac{\sum_{i=1}^{d} a_i b_i}{\sqrt{\sum_{i=1}^{d} a_i^2} \cdot \sqrt{\sum_{i=1}^{d} b_i^2}}$$

**Cosine Distance (used by pgvector `<=>` operator):**

$$\text{dist}(\mathbf{A}, \mathbf{B}) = 1 - \text{sim}(\mathbf{A}, \mathbf{B})$$

**Course Anchoring Decision Rule:**

$$\text{action}(g) = \begin{cases} \text{MODIFY} & \text{if } \max_j \text{sim}(g, c_j) > 0.60 \\ \text{ELECTIVE} & \text{if } 0.40 \leq \max_j \text{sim}(g, c_j) \leq 0.60 \\ \text{NEW COURSE} & \text{if } \max_j \text{sim}(g, c_j) < 0.40 \end{cases}$$

**Alignment Score (Tier 1):**

$$\text{AlignmentScore} = \frac{1}{|G_{matched}|} \sum_{g \in G_{matched}} \text{sim}(\mathbf{H}_{track}, \mathbf{H}_{g}) \times 100\%$$

### 3.4.5.4 Time Complexity

| Operation | Complexity |
|---|---|
| Dot product per pair | O(d) |
| Norm computation | O(d) |
| All courses for one gap | O(M × d) |
| **All gaps, all courses (in-memory)** | **O(G × M × d)** |
| **pgvector ANN search (HNSW)** | **O(log N)** per query |

where G = number of true gaps (~10–50), M = courses per track (~30–80), d = 448, N = job embeddings in pgvector (up to 10,000). In-memory course anchoring completes in milliseconds. pgvector job matching uses HNSW index for sub-millisecond ANN queries.

---

## 3.4.6 XGBRanker (LambdaMART)

XGBRanker implements the LambdaMART Learning-to-Rank algorithm via the XGBoost framework, which directly optimizes listwise ranking metrics — specifically Normalized Discounted Cumulative Gain (NDCG) — rather than minimizing a classification or regression loss. In TechGap, XGBRanker serves as the Adaptive Ranking Engine (Phase 6), sorting the list of identified True Gap skills into a priority-ordered action plan. Each gap skill is represented as a feature vector containing three ranking signals: Industry Demand Weight (how frequently the skill appears across scraped job postings), Gap Severity (the cosine distance between the curriculum and the industry skill embedding), and Bloom's Taxonomy Level (the cognitive depth at which the skill is required). For the initial version (v1), when no expert-labeled ranking data is available, synthetic relevance labels are derived from a composite formula combining these three signals and scaled to integer grades of 0 to 4. XGBRanker is trained on these synthetic labels and replaced by a model trained on curriculum expert-labeled examples once 50 or more labeled gap priority samples become available.

### 3.4.6.1 Implication of XGBRanker in the System

XGBRanker implements the LambdaMART Learning-to-Rank algorithm and serves as the Adaptive Ranking Engine (Phase 6) in TechGap. It sorts the identified True Gaps into a priority-ordered action plan by combining three signals: Industry Demand Weight (how frequently the skill appears in job postings), Gap Severity (the cosine distance between curriculum and industry skill), and Bloom's Taxonomy Level (cognitive depth of the required skill).

Unlike a simple weighted sum, LambdaMART directly optimizes the NDCG (Normalized Discounted Cumulative Gain) ranking metric, ensuring the most urgent gaps appear at the top of the dashboard where curriculum developers focus their attention first. For v1 without expert-labeled data, synthetic relevance labels are derived from the composite formula; XGBRanker is retrained as expert labels become available.

### 3.4.6.2 Pseudocode

```
1.  Input: True gaps G = {g_1..g_N} each with features:
        f(g) = [demand_weight, gap_severity, bloom_level, course_flexibility]
2.  Generate synthetic relevance labels (v1 baseline):
3.      For each gap g_i do
4.          rel_i = demand_weight_i * (1 - sim_i) * bloom_level_normalized_i
5.          rel_i = round(rel_i * 4)  // scale to 0-4 relevance grades
6.      End For
7.  Initialize XGBRanker model with objective = "rank:ndcg"
8.  Training (T boosting rounds):
9.      Initialize base score F_0(g) = 0 for all gaps
10.     For t = 1 to T do
11.         For each pair (g_i, g_j) where rel_i > rel_j do
12.             s_ij = F_{t-1}(g_i) - F_{t-1}(g_j)
13.             delta_NDCG_ij = |NDCG change from swapping positions of g_i and g_j|
14.             lambda_ij = delta_NDCG_ij * sigma(-s_ij)
15.         End For
16.         Compute per-gap lambda: lambda_i = sum_j(lambda_ij) - sum_j(lambda_ji)
17.         Fit regression tree h_t to pseudo-residuals {lambda_i}
18.         Update: F_t(g) = F_{t-1}(g) + eta * h_t(g)
19.     End For
20. Inference:
21.     For each gap g in new pipeline run do
22.         urgency_score(g) = F_T(g)
23.     End For
24.     Sort gaps by urgency_score descending
25. Return ranked gap list with urgency scores
```

*Figure 3.4.6.2 Pseudocode of XGBRanker (LambdaMART) Algorithm*

The XGBRanker training procedure learns to order True Gap skills by urgency. The process starts by accepting the set of True Gaps, each described by a feature vector of industry demand weight, gap severity, Bloom's level, and course flexibility. Because expert-labeled ranking data is unavailable in v1, synthetic relevance labels are generated for each gap by multiplying its demand weight, gap severity, and normalized Bloom's level together, then scaling the product to integer relevance grades between 0 and 4. The XGBRanker model is initialized with the `rank:ndcg` objective, which instructs XGBoost to optimize NDCG directly. Training proceeds over T boosting rounds. In each round, the algorithm computes a score difference for every pair of gaps where one has a higher relevance label than the other. A lambda gradient is calculated for each such pair, weighted by both the absolute NDCG change that would result from swapping the pair's ranking positions and the sigmoid of the negative score difference — this gradient quantifies the force needed to push the higher-relevance gap above the lower-relevance one. The per-gap net lambda is aggregated from all pairs involving that gap. A regression tree is fit to these pseudo-residuals, and the boosted model is updated by adding the tree's predictions scaled by the learning rate. At inference time, the trained model assigns an urgency score to each True Gap in a new pipeline run, and the gaps are sorted in descending order of urgency score to produce the final prioritized action plan delivered to the dashboard.

### 3.4.6.3 Formula and Mathematical Computations

**Pairwise Score Difference:**

$$s_{ij} = F(g_i) - F(g_j)$$

**Lambda Gradient (force pushing g_i above g_j):**

$$\lambda_{ij} = |\Delta\text{NDCG}_{ij}| \cdot \sigma(-s_{ij}) = |\Delta\text{NDCG}_{ij}| \cdot \frac{1}{1 + e^{s_{ij}}}$$

**Per-Item Lambda (net ranking force):**

$$\lambda_i = \sum_{j: rel_i > rel_j} \lambda_{ij} - \sum_{j: rel_j > rel_i} \lambda_{ji}$$

**NDCG (Normalized Discounted Cumulative Gain):**

$$\text{DCG}@k = \sum_{i=1}^{k} \frac{2^{rel_i} - 1}{\log_2(i + 1)}, \quad \text{NDCG}@k = \frac{\text{DCG}@k}{\text{IDCG}@k}$$

where IDCG@k is the DCG of the ideal (perfect) ranking.

**Synthetic Relevance Label (v1 baseline, no expert data):**

$$rel_i = \left\lfloor \left( w_d \cdot \text{demand}_i + w_s \cdot (1 - \text{sim}_i) + w_b \cdot \frac{\text{bloom}_i}{6} \right) \times 4 \right\rfloor$$

where w_d, w_s, w_b are importance weights (default: 0.5, 0.3, 0.2) and the result is scaled to integer grades 0–4.

**Boosted Model Update:**

$$F_t(g) = F_{t-1}(g) + \eta \cdot h_t(g)$$

where η is the learning rate and h_t is the t-th regression tree.

### 3.4.6.4 Time Complexity

| Operation | Complexity |
|---|---|
| Pairwise lambda computation | O(N² × T) |
| Tree fitting per round | O(N × log N) |
| **Full training (T rounds)** | **O(T × N² + T × N × log N)** |
| **Inference (scoring N gaps)** | **O(T × N)** |

where N = number of true gaps (typically 10–50 per track), T = boosting rounds (default 100). Given the small N, training completes in under 1 second. The quadratic pairwise term is negligible at this scale.

---

## 3.4.7 TOPSIS (v1 Ranking Baseline)

TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) is a deterministic multi-criteria decision-making algorithm that ranks a set of alternatives by measuring each alternative's geometric distance from a hypothetical ideal best solution and from a hypothetical ideal worst solution. The alternative closest to the ideal best and farthest from the ideal worst receives the highest rank. In TechGap, TOPSIS functions as the deterministic v1 baseline for the Adaptive Ranking Engine, operating before XGBRanker is trained on expert-labeled gap priority data. It ranks the identified True Gap skills using three criteria: Industry Demand Weight, Gap Severity (cosine distance between curriculum and industry skill embedding), and Bloom's Taxonomy Level. TOPSIS requires no training data and produces a fully transparent, auditable ranking — a property essential for CHED compliance reporting where academic stakeholders must be able to independently verify and trace every recommendation. Once 50 or more expert-labeled gap priority examples are collected from curriculum developers, TOPSIS is replaced by XGBRanker for its adaptive learning capability.

### 3.4.7.1 Implication of TOPSIS in the System

TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) is used as the **deterministic v1 baseline** for the Adaptive Ranking Engine, before XGBRanker is trained with expert-labeled gap priority data. It ranks the True Gaps by computing each gap's closeness to a hypothetical ideal solution (maximum demand, maximum severity, maximum Bloom's level) and distance from a negative-ideal solution (minimum on all criteria).

TOPSIS requires no training data and produces a transparent, auditable ranking that academic stakeholders can independently verify — a critical property for CHED compliance reporting. When expert-labeled ranking data becomes available (50+ labeled examples), TOPSIS is replaced by XGBRanker for adaptive learning capability.

### 3.4.7.2 Pseudocode

```
1.  Input: True gaps G = {g_1..g_N}
2.  Input: Decision matrix X where X[i][j] = score of gap i on criterion j
        Criteria j = [demand_weight, gap_severity, bloom_level]  (m=3)
3.  Input: Criterion weights W = [w_1, w_2, w_3] (e.g., [0.5, 0.3, 0.2])
4.
5.  Step 1 — Normalize decision matrix:
6.      For each criterion j = 1 to m do
7.          denom_j = sqrt(sum(X[i][j]^2) for i = 1..N)
8.          For each gap i do
9.              R[i][j] = X[i][j] / denom_j
10.         End For
11.     End For
12.
13. Step 2 — Compute weighted normalized matrix:
14.     V[i][j] = W[j] * R[i][j]
15.
16. Step 3 — Determine ideal best and worst:
17.     For each criterion j do
18.         V_best[j] = max(V[i][j]) for i = 1..N   // all criteria: benefit type
19.         V_worst[j] = min(V[i][j]) for i = 1..N
20.     End For
21.
22. Step 4 — Compute separation distances:
23.     For each gap i do
24.         d_best[i]  = sqrt(sum((V[i][j] - V_best[j])^2) for j = 1..m)
25.         d_worst[i] = sqrt(sum((V[i][j] - V_worst[j])^2) for j = 1..m)
26.     End For
27.
28. Step 5 — Compute closeness coefficient:
29.     For each gap i do
30.         C[i] = d_worst[i] / (d_best[i] + d_worst[i])
31.     End For
32.
33. Step 6 — Rank gaps by C[i] descending (C=1 is ideal, C=0 is worst)
34. Return ranked gap list with closeness scores as urgency scores
```

*Figure 3.4.7.2 Pseudocode of TOPSIS Algorithm*

The TOPSIS algorithm ranks True Gap skills by their composite urgency across three criteria without requiring any training data. The process begins by constructing a decision matrix where each row represents a gap skill and each column represents one of the three criteria: industry demand weight, gap severity, and Bloom's level. In the first step, the decision matrix is normalized column-by-column by dividing each value by the Euclidean norm of its column, ensuring all criteria are placed on a comparable scale regardless of their original units. In the second step, each normalized value is multiplied by its corresponding criterion weight, producing a weighted normalized matrix. The three criteria weights default to 0.5 for demand, 0.3 for severity, and 0.2 for Bloom's level, and are adjustable. In the third step, the ideal best solution is defined as the maximum weighted normalized value across all gaps for each criterion, and the ideal worst solution is the minimum. In the fourth step, the Euclidean distance from each gap to the ideal best and to the ideal worst is computed across all three criteria. In the fifth step, each gap's closeness coefficient is calculated as its distance to the ideal worst divided by the sum of its distances to both the ideal best and ideal worst, yielding a score between 0 and 1. A score of 1 indicates the gap is closest to the ideal (highest urgency), while a score of 0 indicates the lowest urgency. Finally, all gaps are sorted in descending order of their closeness coefficient, producing the prioritized action plan returned to the dashboard.

### 3.4.7.3 Formula and Mathematical Computations

**Step 1 — Normalized Decision Matrix:**

$$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{i=1}^{N} x_{ij}^2}}$$

**Step 2 — Weighted Normalized Matrix:**

$$v_{ij} = w_j \cdot r_{ij}, \quad \sum_{j=1}^{m} w_j = 1$$

**Step 3 — Ideal Best and Worst Solutions:**

$$v_j^{+} = \max_{i} v_{ij}, \quad v_j^{-} = \min_{i} v_{ij} \quad \forall j \in \{1, \ldots, m\}$$

(All three criteria — demand, severity, Bloom's level — are benefit-type: higher is better.)

**Step 4 — Euclidean Separation Distances:**

$$d_i^{+} = \sqrt{\sum_{j=1}^{m} (v_{ij} - v_j^{+})^2}, \quad d_i^{-} = \sqrt{\sum_{j=1}^{m} (v_{ij} - v_j^{-})^2}$$

**Step 5 — Closeness Coefficient (Urgency Score):**

$$C_i = \frac{d_i^{-}}{d_i^{+} + d_i^{-}}, \quad C_i \in [0, 1]$$

A gap with C_i = 1 is closest to the ideal (highest urgency). A gap with C_i = 0 is farthest from ideal (lowest urgency).

**Ranking:**

$$\text{rank}(g_i) = \text{argsort}_{i}\ C_i \quad \text{(descending)}$$

### 3.4.7.4 Time Complexity

| Operation | Complexity |
|---|---|
| Normalization | O(N × m) |
| Weighted matrix | O(N × m) |
| Ideal solutions | O(N × m) |
| Separation distances | O(N × m) |
| Closeness coefficient | O(N) |
| Sorting | O(N log N) |
| **Total TOPSIS** | **O(N × m + N log N)** |

where N = number of true gaps (10–50 per track), m = 3 criteria. TOPSIS runs in microseconds — effectively instantaneous regardless of scale. This makes it ideal as a real-time fallback or validation check alongside XGBRanker.

---
## Project-Specific Quantitative Logic

The following items were previously included here but are TechGap-defined metrics or scoring rules rather than standard named algorithms:

- Weighted Student Profile Aggregation
- Career-Role Suggestion Scoring
- Student Roadmap Sequencing

They have been moved to [Quantitative Gap Analysis Metrics.md](./Quantitative%20Gap%20Analysis%20Metrics.md) and [Admin Quantitative Metrics.md](./Admin%20Quantitative%20Metrics.md).

---
## Algorithms Excluded (Insufficient Formal Structure)

The following algorithms from `ALGORITHMS.md` are **excluded from this document** because they lack one or more of the required components (pseudocode, mathematical formula, time complexity):

| Algorithm | Reason for Exclusion |
|---|---|
| spaCy EntityRuler (Skill Extraction) | No mathematical formula — purely rule/pattern-based string matching |
| Rule-Based Subsumption (Inference Engine) | No mathematical formula — graph traversal with if/else logic |
| Bloom's Taxonomy Verb Classifier | No mathematical formula — deterministic verb-to-level lookup table |
| Seniority Level Extractor | No mathematical formula — regex/token pattern matching |
| CHED Compliance Guardrails | No mathematical formula — deterministic regulatory rule engine |

All of the above are documented with rationale and pseudocode equivalents in `ALGORITHMS.md`.
