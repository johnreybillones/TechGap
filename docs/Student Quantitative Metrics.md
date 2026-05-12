## **3.5 Student Quantitative Metrics**

## 

To support personalized student-side analysis, the system employs several quantitative models that operate on mastered courses, current progression, and selected career targets. Unlike the admin/faculty metrics, these computations are based on **partial and user-varying curriculum evidence**, making them suitable for personalized guidance rather than full-program audit. The student-side metrics cover profile construction, career-role suggestion scoring, personal alignment, and roadmap sequencing.

#### **3.5.1 Weighted Student Profile Aggregation**

The Weighted Student Profile Aggregation model converts a student's mastered courses into one unified profile vector. This allows the system to compare the student's partial academic evidence against career-role demand profiles in a mathematically consistent way. The formula is defined as:

Course Weight = αui + βbi  
Where:

* ui represents the normalized units or load weight of course i.  
* bi represents the normalized Bloom-depth weight of course i.  
* α and β are weighting coefficients such that α + β = 1.  

The aggregated student profile is then computed as:

Student Profile = (Σ wi hi / Σ wi)  
Where:

* wi is the computed weight of course i.  
* hi is the hybrid embedding of course i.  
  The resulting profile is normalized before downstream comparison so that student-side similarity scores remain comparable across different users and varying numbers of mastered courses.

#### **3.5.2 Career-Role Suggestion Scoring**

The Career-Role Suggestion Scoring model ranks eligible student-facing career options using the student's aggregated profile. It combines semantic similarity with demand and evidence strength to generate the top suggestions shown in the student flow. The score is defined as:

Career Role Score = γsj + δdj + εej  
Where:

* sj is the cosine similarity between the student's normalized profile and the role demand profile.  
* dj is the normalized demand weight of role j.  
* ej is the normalized evidence confidence of role j.  
* γ, δ, and ε are weighting coefficients such that γ + δ + ε = 1.  
  The system sorts the resulting scores in descending order and returns the top-ranked career-role suggestions. These suggestions remain personalized because they depend on the student's mastered-course evidence and current academic progression.

#### **3.5.3 Personal Alignment Score**

The Personal Alignment Score measures how closely a student's current mastered-course profile aligns with the selected career target. Unlike admin metrics, this score does not assume full curriculum completion; it reflects only the student's present or self-declared mastered evidence. The formula is defined as:

Personal Alignment Score = cos(p, qrole) * 100%  
Where:

* p is the normalized student profile vector.  
* qrole is the normalized demand profile of the selected career role.  
  This metric is used to categorize student alignment into interpretable bands such as strong, moderate, or weak alignment, helping students understand how close they currently are to their selected path.

#### **3.5.4 Student Roadmap Sequencing**

The Student Roadmap Sequencing model orders recommended skill-development steps so that urgency and prerequisite structure are both respected. Rather than treating all missing competencies as a flat list, the system chooses the next valid roadmap node from the currently available prerequisite-safe set. The selection rule is:

Next Roadmap Node = argmax g∈At u(g)  
Where:

* At is the set of currently available nodes with no unresolved prerequisites.  
* u(g) is the urgency score assigned to roadmap node g.  
  This ensures that the student roadmap remains pedagogically valid while still prioritizing the most important skill gaps first.

#### **3.5.5 Student-Side Interpretation Note**

These student-side metrics are intentionally based on incomplete and user-varying evidence. Year level, irregular status, and mastered-course selection can all change the resulting analysis. For that reason, these formulas should be interpreted as **personalized guidance metrics**, not as substitutes for the full-curriculum admin evaluation metrics documented in [Admin Quantitative Metrics.md](./Admin%20Quantitative%20Metrics.md).
