# TechGap Documentation Index

> Purpose: Entry point for repository documentation during the Markdown migration.
> Canonical for: Documentation structure, current document map, and migration flow.
> Related: [MIGRATION_APPROVAL_MANIFEST.md](./MIGRATION_APPROVAL_MANIFEST.md), [../CLAUDE.md](../CLAUDE.md)

## Current State

The repository is in migration Pass 1.

- Existing Markdown files remain in place.
- Duplicate content has not been removed or merged yet.
- Approval-gated merge work is tracked in [MIGRATION_APPROVAL_MANIFEST.md](./MIGRATION_APPROVAL_MANIFEST.md).

## Planned Structure

- [product/product-documents.md](./product/product-documents.md): product requirements, output specs, and use cases
- [architecture/architecture-documents.md](./architecture/architecture-documents.md): system design, pipeline, algorithms, and ADRs
- [implementation/implementation-documents.md](./implementation/implementation-documents.md): status, timeline, and implementation plans
- [reference/reference-documents.md](./reference/reference-documents.md): external or source-reference material
- [archive/archive-policy.md](./archive/archive-policy.md): retired or superseded documentation

## Active Documents

- Product and scope:
  - [PRD.md](./PRD.md)
  - [PRD_Detailed.md](./PRD_Detailed.md)
  - [use_case.md](./use_case.md)
- Architecture and algorithms:
  - [Model.md](./Model.md)
  - [ALGORITHMS.md](./ALGORITHMS.md)
  - [ALGORITHMS_FORMAL.md](./ALGORITHMS_FORMAL.md)
- Delivery and status:
  - [technical_plan_status.md](./technical_plan_status.md)
  - [Timeline.md](./Timeline.md)
  - [subtasks/1.1 Supabase Environment Setup.md](./subtasks/1.1%20Supabase%20Environment%20Setup.md)
  - [subtasks/1.2 Adzuna FastAPI Service Implementation.md](./subtasks/1.2%20Adzuna%20FastAPI%20Service%20Implementation.md)
  - [subtasks/1.3 Scraping_Implementation_Plan.md](./subtasks/1.3%20Scraping_Implementation_Plan.md)
- Regulatory and reference:
  - [CHED Memo.md](./CHED%20Memo.md)
  - [SAMPLE_ALGORITHMS_FORMAL.md](./SAMPLE_ALGORITHMS_FORMAL.md)

## Migration Rules

- Do not merge duplicate sections without explicit cluster approval.
- Do not delete or move existing Markdown files during Pass 1.
- When Pass 2 begins, merge by approved cluster only and replace duplicate detail with short links.
