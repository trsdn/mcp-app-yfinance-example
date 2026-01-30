# ADR-004: Period Change vs Daily Change

**Status:** Accepted  
**Date:** 2026-01-30

## Context

Users expect "6 month change" to show performance over the full period, not just today's change.

## Decision

Calculate change as `(currentPrice - periodStartPrice) / periodStartPrice * 100`.

## Consequences

- (+) Accurate period performance
- (+) Consistent with financial apps
- (-) Requires history data to compute
