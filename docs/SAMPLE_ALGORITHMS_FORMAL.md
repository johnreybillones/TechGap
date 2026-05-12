## **3.4 Algorithms and Its Rules**

### **3.4.1 Sentence-BERT (SBERT)**

Sentence-BERT (SBERT) is described as a transformer-based deep learning model primarily developed to create fixed-length global semantic representations of textual inputs. In contrast to classic BERT, which provides contextualized token-level outputs, the SBERT model uses a Siamese-like architecture to quickly compute the embeddings of sentences, thus grasping the semantic similarity. In TechGap, SBERT is the primary representation learning method, which converts the job descriptions and curriculum text into 384-dimensional dense vectors. After the embeddings are generated, the system can determine the semantic relationships by means of clustering, similarity scoring, and then classification tasks based on the obtained similarity, thereby linking academic content and industry requirements.

#### **3.4.1.1 Implication of SBERT in the System**

SBERT transforms complicated text data into a mathematically comparable format that the system can operate with, thus enabling the platform to conduct upper-level reasoning on job roles and curriculum content. SBERT harnesses the power of embedding text into a continuous vector space, which means that even the subtlest differences in the meaning of the words are reflected. This aspect helps to improve the accuracy of job-family clustering, the sensitivity of similarity detection in the Siamese Network, and the trustworthiness of Logistic Regression classification. The system, in the absence of SBERT, would be dependent on features that are sparse or based on keywords, which means that the semantic depth would be lacking, and this would greatly limit the system's capability of recognizing real alignment or gaps in technical competencies.

#### **3.4.1.2 Pseudocode**

Input: Collection of text documents (curriculum and job descriptions)  
Output: Semantic embeddings for each text document

1\. Initialize the pretrained SBERT model  
2\. For each text document in the dataset do  
3\. Clean the text  
4\. Encode the text using SBERT  
5\. Normalize and store the embedding  
6\. End For  
7\. Return all text embeddings

##### **_Figure 2.1.1.2 Pseudocode of SBERT Algorithm_**

The SBERT algorithm converts unstructured text into fixed-length semantic embeddings that capture contextual meaning. First, the pretrained SBERT model is initialized. Each text document in the dataset is then processed sequentially. Before encoding, the text is cleaned to remove noise and ensure consistency. The cleaned text is passed through the SBERT model to generate a dense numerical embedding. The resulting embedding is normalized to ensure consistent magnitude across vectors. This process is repeated for all text documents, and the collection of embeddings is returned for downstream analysis.

#### **3.4.1.3 Formula and Mathematical Computations**

Given a text input t, SBERT generates an embedding vector:

v=fSBERT(t)  
where v ∈ R^384

Similarity between two texts is computed using cosine similarity:

    sim(v1, v2) \= v1  v2||v1|| ||v2||

#### **3.4.1.4 Time Complexity**

Sentence-BERT (SBERT) is built upon the transformer architecture, which theoretically exhibits quadratic time complexity with respect to the input token length due to the self-attention mechanism. For an input sequence of length L, the self-attention computation has a complexity of O(L2)

However, in the TechGap system, SBERT is used only for inference on short, bounded-length text inputs such as curriculum descriptions and job postings. Since the maximum token length is fixed by the pretrained model and does not grow with the dataset size, the cost of encoding a single text sample can be treated as constant.

Let n denote the number of text samples to be encoded. The overall practical time complexity of SBERT embedding generation in TechGap is therefore:

O(n)

This makes SBERT scalable for processing large collections of curriculum and job-market texts within the system.

###

### **3.4.2 K-Means Clustering**

K-Means clustering is a type of unsupervised machine learning algorithm that segments data points into k clusters through the reduction of the within-cluster variance. In TechGap, K-Means is used on the SBERT embeddings of job descriptions for the automatic formation of job families, thus condensing thousands of job listings into consistent cluster groups. The cluster label now represents the "auto-labeled job family," which is employed by the Siamese Network for contrastive training and by Logistic Regression for job-family classification.

#### **3.4.2.1 Implication of K-Means in the System**

K-Means gives the system a structured method of comprehension of the job market landscape without the need for manually labeled data. This clustering stage allows TechGap to unveil the naturally occurring associations among the related roles, thus increasing the accuracy of the positive/negative pair creation by the Siamese Network. It further provides interpretable labels (Cluster_0 … Cluster_7) which the Logistic Regression model can learn to anticipate from the curriculum content. In short, K-Means is the principle that categorizes job roles into significant semantic families.

#### **3.4.2.2 Pseudocode**

    	Input: SBERT embeddings of job descriptions, number of clusters K

Output: Cluster label assigned to each job description

1\. Initialize k cluster centroids  
2\. Repeat until convergence do  
3\. Assign each embedding to the nearest centroid  
4\. Update each centroid as the mean of its assigned embeddings  
5\. End Repeat  
6\. Return cluster labels for all job descriptions

##### **_Figure 2.1.2.2 Pseudocode of K-Means Algorithm_**

K-Means clustering groups job description embeddings into a predefined number of clusters based on semantic similarity. Initially, a set of cluster centroids is randomly initialized. The algorithm then iteratively assigns each embedding to the nearest centroid using a distance metric. After assignment, each centroid is updated by computing the mean of all embeddings assigned to it. These steps are repeated until the centroids stabilize or convergence is achieved. The final output is a cluster label assigned to each job description, representing its corresponding job family.

####

#### **3.4.2.3 Formula and Mathematical Computations**

K-Means optimizes the objective:

Ci=1 kxCi ||x-i||2

    where:
    	X \= SBERT embedding of a job description
    	C*i* \= cluster *i*
    	***μi*** **\=** centroid of cluster *i*

    Centroid update rule:

i=1|Ci|xCix

#### **3.4.2.4 Time Complexity**

K-Means clustering assigns each data point to the nearest cluster centroid and iteratively updates the centroids until convergence. For a dataset containing n SBERT embeddings of dimension d, clustered into k groups over i iterations, the time complexity is:

O(nkdi)  
   
In the context of TechGap:

- n \= number of job descriptions
- k \= 8 (fixed number of clusters)
- d \= 384 (fixed SBERT embedding dimension)
- i is small and bounded due to rapid convergence  
  Since k, d, i are constants, the overall time complexity simplifies to:

O(n)

Thus, K-Means clustering operates in linear time with respect to the number of job descriptions processed.

###

### **3.4.3 Siamese Neural Network**

The Siamese Neural Network is a deep learning architecture that employs two inputs processed by similar subnetworks to generate similar embeddings. In TechGap, SBERT embeddings are input to a projection network which gives back the normalized 128-dimensional vectors. The model is trained with positive job pairs (same cluster) and negative pairs (different clusters) using a contrastive loss function. This learning method allows the system to closely determine the semantic similarity between curriculum content and job roles.

#### **3.4.3.1 Implication of the Siamese Network**

The Siamese Network is an advanced version of SBERT which, instead of the usual embeddings, learns distinctive similarity relationships specific to the job-market field through a process called embedding refinement. Consequently, the Semantic vectors that are more discriminative and could successfully tell apart the closely related job roles are produced. The Siamese Network at the time of inference does similarity scoring between the vectors of the curriculum and those of the job-role directly supporting the system's matching and alignment outputs. The Network is capable of relational structure modeling which is a very important factor in the process of determining the job roles that best match a certain curriculum.

#### **3.4.3.2 Pseudocode**

Input:  
 Pairs of text documents (positive and negative pairs)  
 Pretrained SBERT model

Output: Trained Siamese Network for similarity scoring

1\. Construct training pairs from clustered job descriptions  
2\. Initialize Siamese projection network  
3\. For each training epoch do  
4\. For each text pair do  
5\. Encode both texts using SBERT  
6\. Project and normalize both embeddings  
7\. Compute cosine similarity  
8\. Compute contrastive loss  
9\. Update network parameters  
10\. End For  
11\. End For  
12\. Return trained Siamese Network

##### **_Figure 2.1.3.2 Pseudocode of Siamese Neural Network Algorithm_**

The Siamese Neural Network learns a task-specific similarity function by comparing pairs of text documents. Training pairs are constructed from clustered job descriptions, where pairs from the same cluster are labeled as similar and pairs from different clusters are labeled as dissimilar. A projection network is initialized to transform SBERT embeddings into a lower-dimensional similarity space. During training, each pair of texts is encoded using SBERT, projected, and normalized. The cosine similarity between the projected embeddings is computed, and a contrastive loss function is applied to guide learning. Network parameters are updated iteratively over multiple epochs. The trained Siamese Network is returned and later used for similarity scoring between curriculum and job descriptions.

#### **3.4.3.3 Formula and Mathematical Equations**

Given SBERT embeddings v1,v2, the Siamese projection network computes:

z1=g(v1), z2=g(v2)

where g(⋅) is a fully connected neural network.

Contrastive cosine embedding loss:

| _L_ \= | {   | 1 \- (z1, z2), if positive pair (0,(z1,z2)-m), if negative pair |
| :----- | :-- | :-------------------------------------------------------------- |

where m is the margin.

#### **3.4.3.4 Time Complexity**

The Siamese Neural Network in TechGap operates on pairs of text samples. Each training pair consists of two SBERT-encoded inputs that are passed through a shared projection network.

For a single input vector:

- SBERT encoding cost is O(L), where L is bounded
- Projection network cost is O(dh)  
  Thus, the per-pair processing cost is:

O(L+dh)

Let p denote the number of training pairs. Since both positive and negative pairs are generated from clustered job descriptions, the number of training pairs grows quadratically with the dataset size:

pn2

Therefore, the overall training time complexity of the Siamese Neural Network is:

O(n2)

This quadratic complexity is intrinsic to pairwise similarity learning and is acceptable in TechGap because Siamese training is performed offline and only once during model preparation.

### **3.4.4 Logistic Regression**

Logistic Regression, a method of supervised machine learning, is applied in this project for multi-class classification. It operates on SBERT embeddings to find out the K-Means job cluster that is nearest to a curriculum track. The method gives weight coefficients to all the classes, and thus it can give probable outputs that indicate the level of confidence in the allocated job family. This predictive power makes it possible to do profiling and validating of the curriculum in the TechGap platform.

#### **3.4.4.1 Implication of Logistic Regression**

Logistic Regression is a classifier that is both interpretable and complementary to the Siamese similarity scores through its translation of curriculum text into job-family predictions. The model’s probabilistic outputs (softmax probabilities) support the measurement of the degree of curriculum alignment with the given job clusters. The model thus helps to validate the alignment thereby ensuring that the system recommendations are consistent across both similarity-based and classification-based evaluation methods.

#### **3.4.4.2 Pseudocode**

Input:  
 SBERT embeddings of text documents  
 Corresponding cluster labels

Output: Trained Logistic Regression classifier

1\. Split embeddings into training and testing sets  
2\. Initialize Logistic Regression model  
3\. Train the model on training data  
4\. Predict cluster labels for test data  
5\. Return trained classifier and prediction results

##### **_Figure 2.1.4.2 Pseudocode of Logistic Regression Algorithm_**

Logistic Regression is used to classify text embeddings into predefined job clusters. The SBERT embeddings and their corresponding cluster labels are first divided into training and testing sets. A multi-class Logistic Regression model is initialized and trained using the training data through iterative optimization. After training, the model predicts cluster labels for the test data, allowing evaluation of classification performance. The trained classifier and its predictions are returned for use in curriculum-to-job mapping.

#### **3.4.4.3 Formula and Mathematical Equations**

For multi-class prediction, Logistic Regression computes:

P(y \= c | x)=ewCTxkj=1 ewjTx  
 Prediction rule:

y \=cP(y=c|x)

#### **3.4.4.4 Time Complexity**

Training a multi-class Logistic Regression model involves iterative optimization over the dataset. Given:

- n \= number of samples
- d \= embedding dimension
- k \= number of clusters
- t \= training iterations

The training complexity is:

O(tndk)

In TechGap:

- d \= 384 (constant)
- k \= 8 (constant)
- t is bounded  
  Thus, the overall training complexity simplifies to:  
  O(n)​  
  Inference involves a single matrix multiplication and softmax operation, resulting in constant-time prediction per sample.
