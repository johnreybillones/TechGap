# Quantitative Metrics Explained

This document explains the main student-side and admin-side quantitative computations in plain language. It summarizes what each formula measures, what its symbols mean, and how to interpret the result.

The student metrics evaluate one student's current mastered-course profile against a selected career role. The admin metrics evaluate a full curriculum track against industry demand.

## Student Metrics

### Weighted Student Profile

```text
Course Weight = alpha(ui) + beta(bi)
Student Profile = (sum of wi * hi) / (sum of wi)
```

- `ui` is the normalized units or load weight of course `i`
- `bi` is the normalized Bloom-depth weight of course `i`
- `wi` is the computed weight of course `i`
- `hi` is the hybrid embedding of course `i`

This computation gives stronger courses more influence when building the student's overall profile. The final profile is one combined vector representing what the student currently appears to know.

### Career-Role Suggestion Score

```text
Career Role Score = gamma(sj) + delta(dj) + epsilon(ej)
```

- `sj` is the similarity between the student profile and role `j`
- `dj` is the normalized demand weight of role `j`
- `ej` is the normalized evidence confidence of role `j`

This computation ranks career roles by combining student-role similarity, labor-market demand, and supporting job evidence. Higher scores mean the role is both a stronger fit and better supported by the dataset.

### Personal Alignment Score

```text
Personal Alignment Score = cos(p, qrole) * 100%
```

- `p` is the normalized student profile vector
- `qrole` is the normalized demand profile of the selected role

This computation measures how closely the student's current profile matches the chosen role. The result is turned into a percentage so the alignment is easier to explain to students.

### Personal Gap Classification

```text
Present: similarity >= 0.60
Partial: 0.40 <= similarity < 0.60
Missing: similarity < 0.40
Future Curriculum Coverage: taught later, but not yet mastered
```

This computation classifies each required role skill into an easy-to-read status. It shows whether the skill is already covered, partly covered, absent, or expected in later courses.

### Roadmap Priority Score

```text
Urgency Score = f(demand, severity, learning depth, prerequisite importance)
```

This computation decides which missing or partial skills matter most right now. A skill gets higher priority when it is important to the selected role, strongly demanded in job evidence, and still far from the student's current profile.

### Student Roadmap Sequencing

```text
Next Roadmap Node = argmax g in At of u(g)
```

- `At` is the set of currently available skills with prerequisites already satisfied
- `u(g)` is the urgency score of skill `g`

This computation chooses the next best skill from the set of skills the student is actually ready to learn. It prevents the roadmap from recommending advanced topics before their foundations.

### Learning Resource Ranking

```text
Resource Score = f(relevance, level match, accessibility, freshness, availability)
```

This computation ranks learning materials for each roadmap node after allowlist filtering. The goal is to surface resources that are not only relevant, but also practical and trustworthy for the student to use next.

## Admin Metrics

### Job Coverage Score

```text
Job Coverage Score = (M / (M + G)) * 100%
```

- `M` is the count of required job skills covered by the curriculum after inference
- `G` is the count of required job skills that still remain as gaps

This computation measures how much of industry demand is covered by the full curriculum track. A higher score means the curriculum is covering more of the skills that employers currently require.

### Curriculum Relevance Score

```text
Curriculum Relevance Score = (M / Ctotal) * 100%
```

- `M` is the count of curriculum skills that are relevant to the target job set
- `Ctotal` is the total number of distinct skills extracted from the full curriculum track

This computation measures how much of the curriculum is actually relevant to industry demand. It helps reveal whether the curriculum is focused or contains too much weakly aligned content.

### Supporting Semantic Alignment

```text
Semantic Alignment = cos(Htrack, mu_k*) * 100%
```

- `Htrack` is the embedding representation of the full curriculum track
- `mu_k*` is the centroid of the matched job-family cluster

This computation is a supporting semantic indicator, not the main admin metric. It shows how close the curriculum track is to the matched job cluster in embedding space, but it should not replace the ratio-based coverage metrics.

## How To Read The Results

Student metrics are personalized guidance metrics. They change depending on mastered-course selection, year level, and chosen role.

Admin metrics are full-track evaluation metrics. They are meant for curriculum review, not for judging one student's readiness.
