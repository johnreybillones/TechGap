## **3.5 Quantitative Gap Analysis Metrics**

## 

To provide actionable insights into the alignment between academic curricula and industry requirements, the system employs two primary mathematical models: the Job Coverage Score and the Curriculum Relevance Score. These metrics are computed within the backend logic and subsequently visualized on the frontend dashboard to facilitate immediate assessment of curriculum effectiveness.

#### **3.5.1 Job Coverage Score**

The Job Coverage Score quantifies the extent to which a specific curriculum meets the skill demands of a target job role. It is a critical indicator of graduate readiness, representing the percentage of required industry skills that are successfully covered by the academic program. The formula is defined as:

Job Coverage \= (MM \+ G)  100%  
Where:

* M represents the count of Matches Found, defined as the set of skills present in both the curriculum and the job description.  
* G represents the count of Critical Gaps, defined as the set of skills required by the job but absent from the curriculum.  
* The denominator (M \+ G) represents the Total Required skills for the job role.  
  This metric is rendered by the system's metrics grid, where it is displayed alongside the raw counts of matches and gaps to provide a complete view of the skill deficit.

  #### **3.5.2 Curriculum Relevance Score**

  While the Job Coverage Score focuses on meeting industry needs, the Curriculum Relevance Score assesses the efficiency of the academic program itself. This metric determines the proportion of the curriculum's skill set that is directly applicable to the selected career path, helping educators identify "bloat" or outdated subjects. The calculation is derived as follows:  
  Curriculum Relevance \= (MCtotal)  100%  
  Where:  
* M is the count of Matches Found (skills relevant to the job).  
* Ctotal is the Total Curriculum Skills, representing the sum of all distinct skills parsed from the syllabus.  
  The system also identifies Irrelevant Skills (I) , calculated as I \=Ctotal-M. These are skills taught in the curriculum that do not map to the target job role. This distinction is visualized in the frontend using a donut chart comparing "Relevant" skills against "Others" to visually demonstrate the density of relevant content within the course material.