# TechGap Frontend Components

> Purpose: Define reusable UI components and behavior contracts for the v1 frontend.

## Component Principles

- Components should be small, named by product purpose, and composed from shadcn/ui primitives where useful.
- Data-heavy components must expose loading, empty, error, and low-confidence states.
- Components should not directly call backend routes unless they are route-level containers. Prefer adapter-driven props.
- Visual variants should use TechGap semantic tokens from `DESIGN.md`.

## App Shell Components

### `BrandHeader`

Purpose: Shows TechGap identity and route-aware actions.

Needs:

- Logo/text mark.
- Current flow label when inside Student or Admin.
- Role switch action.
- Reset action only where relevant.

### `RoleCard`

Purpose: Entry card for Student or Admin/Faculty.

Needs:

- Title.
- Short description.
- Key outputs preview.
- Primary action.
- Accessible focus and hover states.

## Student Components

### `StudentWizardShell`

Purpose: Shared wrapper for guided student steps.

Needs:

- Step indicator.
- Page heading and helper text.
- Main content slot.
- Back, continue, reset, and optional secondary actions.
- Mobile sticky action bar.

### `ProgramYearForm`

Purpose: Captures program and year level.

Needs:

- Program segmented control for `CS` and `IT`.
- Year selection for `1st`, `2nd`, `3rd`, `4th`, and `Irregular`.
- Inline validation.
- Change confirmation behavior when edits invalidate downstream state.

### `CourseSelector`

Purpose: Multi-select mastered courses.

Needs:

- Search.
- Grouping by year.
- Selected count.
- Select/deselect behavior.
- Sparse-evidence warning when no courses are selected.

### `CareerSuggestionCard`

Purpose: Presents a suggested or alternative career role.

Needs:

- Role title.
- Match/evidence summary.
- Evidence confidence.
- Source label: top 5 suggestion or alternative.
- Selected state.

### `CareerAlternativeSearch`

Purpose: Lets students choose a scraped-job-backed role outside the top 5.

Needs:

- Search input.
- Result list.
- Evidence count.
- Empty state for no eligible roles.
- No free-text submission.

### `AlignmentScoreHero`

Purpose: Displays personal alignment score.

Needs:

- Percentage.
- Band: Strong, Moderate, or Weak.
- Selected role context.
- Explanation of score basis.
- Low-confidence or sparse-evidence banner when applicable.

### `SkillCategorySummary`

Purpose: Summarizes Present, Partial, Missing, and Future Curriculum Coverage counts.

Needs:

- Category counts.
- Segmented visual summary.
- Text alternative for accessibility.

### `SkillGapList`

Purpose: Shows skill rows grouped by category.

Needs per skill:

- Skill name.
- Category.
- Demand weight.
- Evidence note.
- Future course tag when applicable.
- Priority indicator for Missing and Partial items.

### `RoadmapNodeList`

Purpose: Shows ordered roadmap nodes.

Needs per node:

- Sequence number.
- Skill name.
- Priority score.
- Category.
- Demand weight.
- Estimated Bloom level.
- Prerequisites.
- Expand action.
- Open resources action.

### `ResourcePanel`

Purpose: Loads and displays cached learning resources for one roadmap skill.

Needs:

- Per-node loading state.
- Resource title, source, tags, level, free/access label, freshness.
- Error state scoped to the node.
- Empty state when no curated resources exist.

## Admin Components

### `AdminDashboardShell`

Purpose: Shared admin page wrapper.

Needs:

- Selected track context.
- Ordered section layout.
- Optional sticky desktop summary.
- Print action access when report payload exists.

### `TrackSelector`

Purpose: Selects one of `CS-IS`, `CS-GD`, `IT-WD`, or `IT-NT`.

Needs:

- Track cards.
- Selected state.
- Unavailable/empty state.
- Change behavior that clears selected job and downstream payloads.

### `TopJobCard`

Purpose: Shows one of the top 5 jobs for a track.

Needs:

- Role title.
- Demand weight.
- Skill overlap summary.
- Evidence count.
- Confidence flag.
- Review evidence action.

### `JobEvidencePanel`

Purpose: Displays evidence for the selected job.

Needs:

- Representative title.
- Deduplicated posting count.
- Extracted skills.
- Demand signals.
- Matched cluster or rationale.
- Source identifiers or links where allowed.
- Loading and error states independent from top jobs list.

### `MetricCard`

Purpose: Displays primary and supporting admin metrics.

Needs:

- Metric name.
- Score.
- Definition summary.
- Interpretation label.
- Optional supporting breakdown.

Primary admin metric cards:

- Job Coverage Score.
- Curriculum Relevance Score.

Supporting metric card:

- Semantic Alignment, only if available.

### `CoverageBreakdown`

Purpose: Displays matched, inferred, missing, and related coverage counts.

Needs:

- Chart or segmented bar.
- Count labels.
- Text summary.

### `BloomDistribution`

Purpose: Shows Bloom level distribution.

Needs:

- L1-L6 labels.
- Count or percentage values.
- Explanation of cognitive-depth relevance.

### `AdminGapTable`

Purpose: Shows ranked true gaps.

Needs per row:

- Skill.
- Urgency score.
- Demand.
- Bloom level.
- Action type.
- Anchor course.
- CHED status.
- Alignment impact when available.

### `ObsolescenceList`

Purpose: Shows low-demand curriculum topics separately from true gaps.

Needs per item:

- Topic.
- Course.
- Current demand.
- Suggested replacement.
- Demand ratio.
- Protection status.

### `PrintableReport`

Purpose: Renders curriculum report content for browser print.

Needs:

- Header with track and generation metadata.
- Current state.
- Recommended changes.
- Projected state.
- Obsolescence report.
- CHED compliance summary.
- Faculty qualification warnings.
- Print CSS compatibility.

## Shared State Components

### `StatusBanner`

Purpose: Communicates warnings and contextual states.

Variants:

- Sparse evidence.
- Low confidence.
- API error.
- Validation error.
- Success/ready.

### `LoadingSkeleton`

Purpose: Keeps async layouts stable.

Rules:

- Skeleton shape should match final content.
- Avoid full-page spinners except for unavoidable first-load states.

### `EmptyState`

Purpose: Explains why content is missing and what to do next.

Needs:

- Clear title.
- Short explanation.
- Recovery action when available.

### `ErrorState`

Purpose: Handles API or adapter failures.

Needs:

- Human-readable message.
- Retry action when safe.
- Technical details hidden by default.

## Chart Components

Use simple, accessible charts before adding complex visualization dependencies.

Required chart types:

- Segmented bars for category distribution.
- Compact horizontal bars for demand or priority ranking.
- Metric cards for scores.
- Optional roadmap graph only if prerequisite relationships are clearer visually than as a list.

All charts need adjacent text summaries.
