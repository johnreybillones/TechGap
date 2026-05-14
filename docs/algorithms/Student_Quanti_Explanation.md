# Student Quantitative Metrics Explained

This document explains the student-side quantitative metrics in plain language. It follows the same student-analysis terms used in [ALGORITHM_PROCESS_DIAGRAM.md](../ALGORITHM_PROCESS_DIAGRAM.md), but it does not include diagrams.

The student metrics are different from the admin/faculty metrics. Admin metrics evaluate a full curriculum track. Student metrics evaluate one student's selected or mastered courses against a target career role.

## Student Metric Inputs

`Compiled curriculum CSV files` provide the course records, syllabus text, CLOs, units, and curriculum metadata. These records tell the system what each course teaches.

`Raw scraped job postings` provide the career-role demand evidence. These postings tell the system what employers currently ask for.

`Skill ontology graph` provides skill relationships. It helps the system understand when one skill is related to, broader than, narrower than, or dependent on another skill.

`Student mastered-course selections` are the courses the student has completed or confidently considers mastered. This is the main student-specific input.

`Selected career role` is the role the student wants to analyze. It can come from the top 5 suggested roles or from another scraped-job-backed career option.

## Weighted Student Profile

`Weighted Student Profile` turns the student's mastered courses into one combined student profile.

Each mastered course contributes to the profile, but not every course contributes equally. A course may receive more weight when it has more units, more contact hours, or deeper Bloom's Taxonomy coverage.

For example, a major programming course with deeper application or creation outcomes should usually affect the profile more than a short introductory course.

The output is one student profile vector. This vector represents what the student currently appears to know based on their mastered-course selections.

## Career-Role Suggestion Score

`Career-Role Suggestion Score` ranks possible career roles for the student.

The system compares the student's profile against each eligible career-role demand profile. A role scores higher when the student's mastered courses are more similar to the role's required skills.

The score can also consider market demand and evidence strength. A role with many supporting job postings and clear extracted skills is more reliable than a role with weak or sparse evidence.

The output is the ranked list of suggested career roles, usually shown as the student's top 5 recommendations.

## Personal Alignment Score

`Personal Alignment Score` measures how close the student's current profile is to the selected career role.

A higher score means the student's mastered courses are more aligned with the role's required skills. A lower score means the student has more distance to cover before the role is well supported by their current academic evidence.

This score is personalized. Two students in the same program can receive different alignment scores because they may select different mastered courses, have different year levels, or target different career roles.

The score should be shown as guidance, not as a final judgment of ability. It reflects available curriculum and job-posting evidence, not every skill the student may have learned outside school.

## Personal Gap Classification

`Personal Gap Classification` explains each required skill for the selected role.

`Present` means the student's mastered courses already provide strong evidence for the skill.

`Partial` means the student has some related evidence, but the coverage may not be deep or direct enough yet.

`Missing` means the student's mastered courses do not provide enough evidence for the skill.

`Future Curriculum Coverage` means the skill appears in the student's curriculum later, but it is not yet part of the student's mastered-course selections.

The skill ontology can adjust these classifications. For example, if a student has mastered a closely related child or parent skill, the system may avoid treating the target skill as completely missing.

## Roadmap Priority Score

`Roadmap Priority Score` helps decide which missing or partial skills should be addressed first.

A skill receives higher priority when it is important to the selected career role, appears often in job evidence, has a large personal gap, or is needed before other skills.

The score prevents the roadmap from becoming a random list of missing skills. It helps the system focus on the gaps that matter most for the student's selected path.

## Student Roadmap Sequencing

`Student Roadmap Sequencing` turns the student's priority gaps into an ordered learning path.

The roadmap does not simply sort every missing skill by urgency. It also checks prerequisite order. Foundational skills should appear before skills that depend on them.

For example, a roadmap should usually place JavaScript fundamentals before React, and networking basics before advanced network security.

The output is a sequence of roadmap nodes that balances urgency with learning order.

## Learning Resource Ranking

`Learning Resource Ranking` attaches recommended resources to each roadmap node.

The system filters resources through trusted or allowlisted sources, then ranks them using metadata such as relevance, skill level, accessibility, freshness, and availability.

This keeps the student experience practical. The analysis does not only say what is missing; it also points the student toward resources that can help close each gap.

## How To Interpret The Metrics

These metrics are intended for personalized student guidance.

They should help students answer:

- Which career roles currently match my mastered courses?
- How aligned am I with my selected role?
- Which skills are already present, partial, missing, or covered later?
- What should I learn next?
- Which resources can help me close the gap?

They should not be treated as a full curriculum audit. Full-track curriculum evaluation belongs to the admin/faculty metrics because that analysis assumes the complete curriculum, not one student's partial progress.
