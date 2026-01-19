# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records for the Small Media project.

## What is an ADR?

An ADR documents a significant architectural decision made during the project, including:
- The context and problem being addressed
- The decision made
- The consequences (positive and negative)

## ADR Index

| Number | Title | Status | Date |
|--------|-------|--------|------|
| [001](./001-technology-stack.md) | Technology Stack Selection | Accepted | 2026-01-19 |
| [002](./002-transcoding-strategy.md) | Hybrid Transcoding Strategy | Accepted | 2026-01-19 |
| [003](./003-playlist-format.md) | YAML Playlist Format | Accepted | 2026-01-19 |

## ADR Template

When creating a new ADR, use this template:

```markdown
# ADR-NNN: Title

## Status
Proposed | Accepted | Deprecated | Superseded by [ADR-XXX](./XXX-title.md)

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?

### Positive
- ...

### Negative
- ...

### Neutral
- ...
```

## Naming Convention

Files should be named: `NNN-short-title.md`
- `NNN`: Three-digit number (001, 002, ...)
- `short-title`: Lowercase with hyphens
