# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the MCP Apps Stock Server.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-sse-transport.md) | SSE Transport over Stdio | Accepted | 2026-01-30 |
| [ADR-003](ADR-003-intraday-intervals.md) | Intraday Intervals for Short Periods | Accepted | 2026-01-30 |
| [ADR-004](ADR-004-period-change.md) | Period Change vs Daily Change | Accepted | 2026-01-30 |

## ADR Template

When adding new ADRs, use this template:

```markdown
# ADR-XXX: Title

**Status:** Proposed | Accepted | Deprecated | Superseded  
**Date:** YYYY-MM-DD

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?
- (+) Positive consequence
- (-) Negative consequence
```
