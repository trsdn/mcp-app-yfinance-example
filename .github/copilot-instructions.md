---
applyTo: '**'
---

# Copilot Instructions for MCP Apps Stock Server

This is an MCP (Model Context Protocol) server project that provides stock market data with interactive UI via MCP Apps.

## Repository Context

- **Main Server**: `server.py` - SSE-based MCP server on port 3002
- **Status**: See `AGENTS.md` for current status and troubleshooting

## Coding Conventions

### Python

- Use `async`/`await` for all MCP handlers
- Use type hints for function parameters and returns
- Follow PEP 8 style guidelines
- Use `yfinance` for stock data fetching

### MCP Server Patterns

When modifying the MCP server:

- Return both `text` and `structuredContent` from tool calls
- Use `text/html;profile=mcp-app` MIME type for UI resources
- Register tools with `_meta={"ui": {"resourceUri": "ui://..."}}`
- Handle SSE connection timeouts gracefully
- Log important events with `[HTTP]` prefix

### HTML/JavaScript (MCP Apps UI)

- Inline all styles and scripts (single-file HTML only)
- Implement `ui/initialize` handshake before receiving data
- Listen for `ui/notifications/tool-result` to get structuredContent
- Use native canvas for charts (no external libraries)
- Support both light and dark themes

## What NOT to Do

- Don't use external CSS or JS files in MCP Apps UI
- Don't embed data in HTML templates — use postMessage
- Don't block on long-running yfinance calls without timeout
- Don't expose API keys or credentials

## Tech Stack

- Python 3.10+ with Starlette/uvicorn
- MCP SDK (`mcp` package)
- yfinance for stock data
- Native canvas for charts
- SSE transport for VS Code connection