# TechGap Page Specifications

> Purpose: Define the screens required for the v1 frontend.

## Global Page Rules

- Every page must show clear current context and next action.
- Every async section needs loading, error, and empty states.
- Every score or category needs a plain-language explanation.
- Low-confidence and sparse-evidence results must be visible, not hidden in tooltips.
- Desktop layouts should be presentation-ready; mobile must support the student journey comfortably.

## `/` - Choose Role

Goal: Let users choose the Student or Admin/Faculty flow without authentication.

Wireframe:

```text
[Brand bar: TechGap]

Hero:
  Headline: Understand curriculum-to-career alignment
  Short explanation of student and faculty use

[Student card]
  Personal alignment, skill gaps, roadmap
  Primary action: Continue as Student

[Admin/Faculty card]
  Track analysis, job evidence, curriculum report
  Primary action: Continue as Admin/Faculty

Footer note:
  v1 is no-auth and demo/session scoped
```

Required states:

- Default state with both roles.
- Role switch return state if user came from another flow.
- No disabled role states in v1.

## `/student` Step 1 - Program And Year Level

Goal: Capture academic context for course filtering.

Wireframe:

```text
[Student wizard shell: Step 1 of 6]

Heading: Start with your academic context
Helper: This controls which curriculum courses appear next.

Program segmented control:
  [CS] [IT]

Year level cards:
  [1st] [2nd] [3rd] [4th] [Irregular]

Actions:
  [Reset] [Continue]
```

Validation:

- Program is required.
- Year level is required.
- Continue is disabled until both are selected or shows inline validation on submit.

Responsive:

- Program control stays horizontal if space allows.
- Year cards collapse into a two-column or single-column mobile grid.

## `/student` Step 2 - Mastered Courses

Goal: Let students select completed or confidently mastered courses.

Wireframe:

```text
[Student wizard shell: Step 2 of 6]

Heading: Select courses you have mastered
Context chip: CS / 3rd year
Helper: Select courses you completed or can confidently apply.

Toolbar:
  Search courses
  Filter by year/group
  Selected count

Course groups:
  Year 1
    [ ] CC101 Course title
    [ ] CC102 Course title
  Year 2
    [ ] ...

Sparse-evidence note if none selected

Actions:
  [Back] [Continue]
```

Validation:

- Empty selection is allowed.
- If empty, show sparse-evidence warning before role suggestions.
- Selected course codes must belong to the filtered course set.

## `/student` Step 3 - Career Role Selection

Goal: Let the student choose a role target from top suggestions or eligible alternatives.

Wireframe:

```text
[Student wizard shell: Step 3 of 6]

Heading: Choose a career target
Helper: Suggestions are based on your mastered courses and job evidence.

Top 5 suggestions:
  [Role card: title, match reason, evidence confidence]
  [Role card]
  ...

Alternative role search:
  Search eligible scraped-job-backed careers
  [Result row with evidence count]

Low-confidence banner when needed

Actions:
  [Back] [Run analysis]
```

Validation:

- Selected role is required before running analysis.
- Alternative role must be from eligible API results; no free-text role submission in v1.
- Low evidence roles show a confidence label.

## `/student` Step 4 - Personal Alignment Analysis

Goal: Show the personal alignment score and explain what it means.

Wireframe:

```text
[Student results shell]

Score hero:
  Personal Alignment: 68%
  Band: Moderate alignment
  Selected role: Frontend Developer
  Evidence confidence label

Explanation:
  What contributes to the score
  What the score does not mean

Summary cards:
  Present skills
  Partial skills
  Missing skills
  Future curriculum coverage

Actions:
  [Review gaps] [Change inputs]
```

Required states:

- Loading analysis.
- Analysis error with retry.
- Sparse-evidence warning when mastered courses are empty or weak.
- Result reveal should use restrained staggered motion.

## `/student` Step 5 - Skill Gap Report

Goal: Group role-required competencies into actionable categories.

Wireframe:

```text
[Gap report]

Category summary segmented bar:
  Present / Partial / Missing / Future Coverage

Category sections:
  Present
    Skill row: demand weight, evidence note
  Partial
    Skill row
  Missing
    Skill row with priority
  Future Curriculum Coverage
    Skill row with future course tag

Actions:
  [Build roadmap] [Back to score]
```

Display rules:

- Each skill shows category, demand weight, and explanation.
- Future-covered skills identify later course(s).
- Missing skills should visually read as priority items without using alarmist copy.

## `/student` Step 6 - Skill Roadmap And Node Resources

Goal: Present a sequenced gap-closing plan.

Resource browsing is part of this step, not a separate student wizard step. Resources load only when the student opens a roadmap node.

Wireframe:

```text
[Roadmap]

Heading: Your recommended skill roadmap
Helper: Ordered by urgency while respecting prerequisites.

Roadmap node list/graph:
  1. Skill name
     Priority score, category, demand weight, Bloom level
     Prerequisites
     [Open resources]

Resource drawer/panel appears when node opens.

Actions:
  [Back to gaps] [Reset]
```

Behavior:

- Nodes are ordered by roadmap sequence.
- Expand/collapse uses Motion layout animation.
- Resources load only when requested.
- Resource errors affect only the selected node, not the whole roadmap.

## `/admin` Section 1 - Track Selector

Goal: Scope all admin analysis to one curriculum track.

Wireframe:

```text
[Admin dashboard shell]

Heading: Curriculum alignment dashboard
Helper: Select a track to evaluate against job-market evidence.

Track cards:
  [CS-IS] [CS-GD] [IT-WD] [IT-NT]

Selected track context persists above downstream sections.
```

Validation:

- Unsupported or unavailable tracks show an empty state, not a crash.
- Changing track clears selected job and downstream payloads.

## `/admin` Section 2 - Top 5 Jobs

Goal: Show the five demand-ranked jobs for the selected track.

Wireframe:

```text
[Top 5 jobs section]

Job card list:
  Role title
  Demand weight
  Skill overlap summary
  Evidence count
  Confidence flag if sparse
  [Review evidence]
```

Behavior:

- Selecting a job opens or updates the evidence panel.
- Evidence-sparse jobs remain visible if returned by the API but are clearly labeled.

## `/admin` Section 3 - Job Evidence Review

Goal: Explain why a job is associated with the selected track.

Wireframe:

```text
[Evidence panel]

Selected role title
Posting count and confidence
Extracted skills
Demand signals
Matched cluster/rationale
Source identifiers or links where allowed
```

Sorting:

- Strongest evidence first by confidence, then demand, then recency if available.

## `/admin` Section 4 - Alignment Dashboard

Goal: Present primary admin metrics and supporting summaries.

Wireframe:

```text
[Metrics grid]

Metric card: Job Coverage Score
  Definition summary
  Score and trend/context if available

Metric card: Curriculum Relevance Score
  Definition summary
  Score and curriculum-efficiency explanation

Supporting cards:
  Skill coverage breakdown
  Bloom distribution
  Top gap preview
  Optional semantic alignment indicator
```

Rules:

- Job Coverage Score and Curriculum Relevance Score are the primary metrics.
- Semantic alignment is supporting only.
- Admin metrics evaluate the full curriculum track.

## `/admin` Section 5 - Gap And Obsolescence Report

Goal: Show ranked true gaps and low-demand curriculum topics.

Data source: use the `/api/admin/report` payload for detailed `recommendedChanges` and `obsolescenceItems`. The dashboard endpoint may show previews, but the canonical endpoint list does not define a separate admin gaps endpoint.

Wireframe:

```text
[Gap and obsolescence]

Priority gaps table/cards:
  Skill
  Urgency
  Demand
  Action type
  Anchor course
  CHED status

Obsolescence section:
  Topic
  Current course
  Demand
  Suggested replacement
  Protection status
```

Behavior:

- Keep high-priority market gaps separate from low-demand curriculum topics.
- Use badges for MODIFY, ELECTIVE, NEW COURSE, and protected/enhance-only states.

## `/admin` Section 6 - Printable Report

Goal: Aggregate admin findings into a print-ready curriculum report.

Data source: use the same `/api/admin/report` payload as the on-screen gap and obsolescence section.

Wireframe:

```text
[Report page/sheet]

Report header:
  Track, generated date, evidence summary

Sections:
  Current state
  Recommended changes
  Projected state
  Obsolescence report
  CHED compliance summary
  Faculty qualification warnings

Actions outside print area:
  [Print / Save as PDF]
  [Back to dashboard]
```

Print rules:

- Hide navigation and non-report controls in print.
- Preserve section headings and page breaks.
- Ensure report is readable in grayscale.
