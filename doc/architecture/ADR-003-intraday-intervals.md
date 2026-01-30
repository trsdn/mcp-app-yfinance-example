# ADR-003: Intraday Intervals for Short Periods

**Status:** Accepted  
**Date:** 2026-01-30

## Context

yfinance returns daily data by default. For 1D and 5D periods, daily granularity is insufficient for meaningful charts.

## Decision

Use period-specific intervals: 1D→5m, 5D→15m, others→1d.

## Consequences

- (+) High-resolution intraday charts
- (+) 1D shows ~78 data points (trading hours)
- (-) More data = larger payloads
