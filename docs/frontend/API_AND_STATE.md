# TechGap Frontend API And State Contracts

> Purpose: Define frontend-facing payloads, mock adapter contracts, and browser state rules.

## Contract Rules

- Page components should depend on typed frontend contracts, not backend implementation details.
- Mock adapters must return the same shapes expected from `/api/*`.
- Real API adapters should be swappable without rewriting page components.
- Errors should normalize into frontend-friendly error objects.
- Dates should use ISO strings.
- Percentages should be numbers from `0` to `100` unless explicitly documented otherwise.

## Shared Types

```ts
type Program = "CS" | "IT";
type YearLevel = "1st" | "2nd" | "3rd" | "4th" | "Irregular";
type TrackCode = "CS-IS" | "CS-GD" | "IT-WD" | "IT-NT";

type ConfidenceLevel = "High" | "Medium" | "Low";
type AlignmentBand = "Strong" | "Moderate" | "Weak";
type SkillCategory = "Present" | "Partial" | "Missing" | "Future Curriculum Coverage";
type GapActionType = "MODIFY" | "ELECTIVE" | "NEW COURSE" | "ENHANCE";

type ApiError = {
  code: string;
  message: string;
  retryable: boolean;
};

type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: ApiError };
```

## Browser State

Storage key: `techgap.student.v1`.

```ts
type StudentSelectionState = {
  version: 1;
  program: Program | null;
  yearLevel: YearLevel | null;
  masteredCourseCodes: string[];
  selectedCareerRoleId: string | null;
  latestAnalysisId?: string | null;
  updatedAt: string;
};
```

Restore rules:

- Missing state starts the wizard at step 1.
- Invalid JSON clears the stored value.
- Unsupported version clears the stored value.
- Invalid program, year level, or course codes are discarded safely.
- If program changes, clear mastered courses, selected role, latest analysis, gaps, roadmap, and resources.
- If year level changes, revalidate mastered courses against the filtered course set.

Reset rules:

- Student Reset removes `techgap.student.v1` and returns to step 1.
- Intentional role switch from Student removes `techgap.student.v1`.

## Mock Adapter Boundary

Implement a frontend adapter interface first:

```ts
type StudentApi = {
  getCourses(input: GetCoursesInput): Promise<ApiResult<GetCoursesResponse>>;
  getCareerSuggestions(input: CareerSuggestionsInput): Promise<ApiResult<CareerSuggestionsResponse>>;
  analyze(input: AnalyzeInput): Promise<ApiResult<AnalyzeResponse>>;
  getRoadmap(input: RoadmapInput): Promise<ApiResult<RoadmapResponse>>;
  getResources(input: ResourcesInput): Promise<ApiResult<ResourcesResponse>>;
};

type AdminApi = {
  getTracks(): Promise<ApiResult<TracksResponse>>;
  getTopJobs(input: TopJobsInput): Promise<ApiResult<TopJobsResponse>>;
  getJobEvidence(input: JobEvidenceInput): Promise<ApiResult<JobEvidenceResponse>>;
  getDashboard(input: DashboardInput): Promise<ApiResult<DashboardResponse>>;
  getReport(input: ReportInput): Promise<ApiResult<ReportResponse>>;
};
```

Pages should receive or import the adapter through a single boundary so mock data can be replaced with real `/api/*` calls later.

## Student API Contracts

### `GET /api/student/courses`

Input:

```ts
type GetCoursesInput = {
  program: Program;
  yearLevel: YearLevel;
};
```

Response:

```ts
type Course = {
  code: string;
  title: string;
  program: Program;
  year: "1st" | "2nd" | "3rd" | "4th";
  units?: number;
  courseType?: "core" | "professional" | "elective" | "GE";
};

type GetCoursesResponse = {
  program: Program;
  yearLevel: YearLevel;
  courses: Course[];
  groupedByYear: Record<string, Course[]>;
};
```

UI states:

- Loading course catalog.
- Empty catalog for unsupported/unloaded data.
- Error with retry.

### `POST /api/student/career-suggestions`

Input:

```ts
type CareerSuggestionsInput = {
  program: Program;
  yearLevel: YearLevel;
  masteredCourseCodes: string[];
};
```

Response:

```ts
type CareerRoleOption = {
  id: string;
  title: string;
  source: "TopSuggestion" | "Alternative";
  score?: number;
  evidenceCount: number;
  confidence: ConfidenceLevel;
  reason: string;
  lowConfidence: boolean;
};

type CareerSuggestionsResponse = {
  suggestions: CareerRoleOption[];
  alternatives: CareerRoleOption[];
  sparseEvidence: boolean;
  warnings: string[];
};
```

Rules:

- `suggestions` should contain up to five top roles.
- Alternatives must be scraped-job-backed.
- No free-text role target is submitted.

### `POST /api/student/analyze`

Input:

```ts
type AnalyzeInput = {
  program: Program;
  yearLevel: YearLevel;
  masteredCourseCodes: string[];
  selectedCareerRoleId: string;
};
```

Response:

```ts
type SkillGapItem = {
  skillId: string;
  skillName: string;
  category: SkillCategory;
  demandWeight: number;
  evidenceNote: string;
  futureCourseCodes: string[];
};

type AnalyzeResponse = {
  analysisId: string;
  selectedRole: CareerRoleOption;
  alignmentScore: number;
  alignmentBand: AlignmentBand;
  sparseEvidence: boolean;
  confidence: ConfidenceLevel;
  gaps: SkillGapItem[];
  categoryCounts: Record<SkillCategory, number>;
  warnings: string[];
};
```

Band rules:

- Strong: `>= 75`.
- Moderate: `>= 50` and `< 75`.
- Weak: `< 50`.

### `POST /api/student/roadmap`

Input:

```ts
type RoadmapInput = {
  analysisId: string;
  selectedCareerRoleId: string;
};
```

Response:

```ts
type RoadmapNode = {
  skillId: string;
  skillName: string;
  priorityScore: number;
  category: "Missing" | "Partial" | "Future Curriculum Coverage";
  prerequisiteSkillIds: string[];
  estimatedBloomLevel: number;
  demandWeight: number;
};

type RoadmapResponse = {
  analysisId: string;
  nodes: RoadmapNode[];
};
```

### `GET /api/resources`

Input:

```ts
type ResourcesInput = {
  skillId: string;
};
```

Response:

```ts
type LearningResource = {
  id: string;
  title: string;
  url: string;
  sourceName: string;
  tags: string[];
  level: "Beginner" | "Intermediate" | "Advanced";
  access: "Free" | "Accessible" | "Unknown";
  refreshedAt: string;
};

type ResourcesResponse = {
  skillId: string;
  resources: LearningResource[];
};
```

Resource loading is scoped to the opened roadmap node.

## Admin API Contracts

### `GET /api/admin/tracks`

```ts
type Track = {
  code: TrackCode;
  name: string;
  programFocus: string;
  available: boolean;
};

type TracksResponse = {
  tracks: Track[];
};
```

### `GET /api/admin/top-jobs`

```ts
type TopJobsInput = {
  track: TrackCode;
};

type TopJob = {
  id: string;
  title: string;
  demandWeight: number;
  skillOverlapSummary: string;
  evidenceCount: number;
  confidence: ConfidenceLevel;
  lowConfidence: boolean;
};

type TopJobsResponse = {
  track: TrackCode;
  jobs: TopJob[];
};
```

### `GET /api/admin/job-evidence`

```ts
type JobEvidenceInput = {
  track: TrackCode;
  jobId: string;
};

type JobEvidenceResponse = {
  track: TrackCode;
  jobId: string;
  representativeTitle: string;
  postingCount: number;
  extractedSkills: string[];
  demandSignals: string[];
  rationale: string;
  sources: Array<{
    label: string;
    url?: string;
  }>;
};
```

### `GET /api/admin/dashboard`

```ts
type DashboardInput = {
  track: TrackCode;
};

type DashboardResponse = {
  track: TrackCode;
  jobCoverageScore: number;
  curriculumRelevanceScore: number;
  semanticAlignmentScore?: number;
  skillCoverage: {
    matched: number;
    inferred: number;
    missing: number;
  };
  bloomDistribution: Record<"L1" | "L2" | "L3" | "L4" | "L5" | "L6", number>;
  topGaps: Array<{
    skillId: string;
    skillName: string;
    demandWeight: number;
    urgencyScore: number;
  }>;
};
```

Rules:

- Job Coverage Score and Curriculum Relevance Score are primary.
- Semantic Alignment is optional and supporting.

### `GET /api/admin/report`

This payload supports both the on-screen gap/obsolescence section and the print-optimized report. The frontend should not invent a separate `/api/admin/gaps` endpoint unless the canonical endpoint plan changes.

```ts
type ReportInput = {
  track: TrackCode;
};

type AdminGap = {
  skillId: string;
  skillName: string;
  urgencyScore: number;
  demandWeight: number;
  bloomLevel: string;
  actionType: GapActionType;
  anchorCourseCode?: string;
  anchorCourseTitle?: string;
  chedStatus: string;
  alignmentDelta?: number;
};

type ObsolescenceItem = {
  topicName: string;
  currentCourseCode: string;
  currentCourseTitle: string;
  industryDemand: number;
  suggestedReplacement: string;
  demandRatio: number;
  chedStatus: string;
};

type ReportResponse = {
  track: TrackCode;
  generatedAt: string;
  currentStateSummary: string;
  recommendedChanges: AdminGap[];
  projectedStateSummary: string;
  obsolescenceItems: ObsolescenceItem[];
  chedComplianceSummary: string;
  facultyQualificationWarnings: string[];
};
```

UI usage:

- `/admin` gap and obsolescence section reads `recommendedChanges` and `obsolescenceItems`.
- The printable report reads the full payload.
- A report fetch error should not clear already loaded dashboard metrics.

## UI State Transitions

Student:

- `idle -> selectingContext -> selectingCourses -> selectingRole -> analyzing -> results -> roadmap`.
- Any context-changing edit from results returns to the earliest affected step and marks previous analysis stale.
- Analysis errors keep the selected inputs and allow retry.

Admin:

- `idle -> selectingTrack -> loadingTrackAnalysis -> dashboardReady`.
- Track change clears job evidence, dashboard payload, gaps, and report payload.
- Job evidence errors do not clear top jobs.
- Report errors do not clear dashboard data.
