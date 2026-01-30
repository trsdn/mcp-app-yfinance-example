```instructions
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
- Handle SSE connection timeouts gracefully
- Log important events with `[HTTP]` prefix

### HTML/JavaScript (MCP Apps UI)

- Inline all styles and scripts (single-file HTML only)
- Wait for tool-result via postMessage before rendering
- Use Chart.js for data visualization
- Support both light and dark themes

## What NOT to Do

- Don't use external CSS or JS files in MCP Apps UI
- Don't block on long-running yfinance calls without timeout
- Don't expose API keys or credentials

## Tech Stack

- Python 3.x with FastAPI/Starlette
- MCP SDK (`mcp` package)
- yfinance for stock data
- Chart.js for charts
- SSE transport for VS Code connection
```