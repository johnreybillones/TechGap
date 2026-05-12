## **3.5 Admin Quantitative Metrics**

## 

To provide actionable insights for curriculum planning and program-level review, the admin/faculty flow employs two primary mathematical models: the Job Coverage Score and the Curriculum Relevance Score. These metrics are computed against the **full curriculum track**, not against a partial student profile, because admin analysis assumes that students complete the curriculum. The metrics are used as the primary quantitative indicators on the admin dashboard and in curriculum evaluation outputs.

#### **3.5.1 Job Coverage Score**

The Job Coverage Score quantifies the extent to which a full curriculum track meets the skill demands of the target job set. It is the primary indicator of how well the curriculum covers required industry competencies after inference is applied. The formula is defined as:

Job Coverage Score = (M / (M + G)) * 100%  
Where:

* M represents the count of Matches Found, defined as required job skills that are covered by the curriculum after inference.  
* G represents the count of Gaps, defined as required job skills that remain absent from the curriculum after inference.  
* The denominator (M + G) represents the Total Required Skills in scope for the target job set.  
  This metric answers the question: "How much of industry demand is covered by the curriculum?" It should be shown as a primary admin dashboard metric because it directly measures curriculum-to-industry coverage strength.

#### **3.5.2 Curriculum Relevance Score**

While the Job Coverage Score focuses on satisfying industry demand, the Curriculum Relevance Score evaluates the efficiency of the curriculum itself. This metric determines the proportion of the curriculum's extracted skill inventory that is directly relevant to the selected job set, helping faculty identify excess, weakly aligned, or outdated content. The calculation is derived as follows:  
Curriculum Relevance Score = (M / Ctotal) * 100%  
Where:

* M is the count of matched curriculum skills that are relevant to the target job set.  
* Ctotal is the Total Curriculum Skills, representing all distinct skills extracted from the full curriculum track.  
  The system may also derive Irrelevant or Non-Targeted Skills as the difference between the full curriculum skill inventory and the matched relevant set. This metric answers the question: "How much of the curriculum is relevant to industry demand?" and complements the Job Coverage Score by revealing curriculum efficiency rather than external coverage alone.

#### **3.5.3 Relationship of the Two Metrics**

The two admin metrics are intentionally kept separate because they answer different evaluation questions:

* **Job Coverage Score** measures external coverage of required industry skills.  
* **Curriculum Relevance Score** measures internal efficiency of the curriculum's own content.  

A curriculum may perform well on one metric and poorly on the other. For that reason, both should appear together in the admin/faculty dashboard and report outputs.

#### **3.5.4 Supporting Semantic Metric**

If a semantic similarity indicator is retained in the admin flow, it should remain a supporting technical metric rather than the primary curriculum-audit metric. A typical supporting form is:

Semantic Alignment = cos(Htrack, μk*) * 100%  
Where:

* Htrack is the embedding representation of the full curriculum track.  
* μk* is the centroid of the matched job-family cluster.  
  This supporting metric can help explain embedding-space similarity trends, but it does not replace the two primary ratio-based admin metrics above.
