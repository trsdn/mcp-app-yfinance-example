# ADR-001: SSE Transport over Stdio

**Status:** Accepted  
**Date:** 2026-01-30

## Context

MCP servers can use stdio or HTTP/SSE transport. VS Code MCP Apps requires the UI to communicate via postMessage, which works better with persistent SSE connections.

## Decision

Use HTTP/SSE transport on port 3002 instead of stdio.

## Consequences

- (+) Enables MCP Apps UI rendering in VS Code chat
- (+) Supports `tools/call` from UI via postMessage
- (-) Requires running server process externally
- (-) Port conflicts possible
