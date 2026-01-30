# Quick Start

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- VS Code Insiders with `chat.mcp.apps.enabled: true`

## Setup

```bash
# Install dependencies
uv sync

# Start the MCP server
uv run python server.py
```

Server starts on `http://localhost:3002/sse`

## VS Code Configuration

Already configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "yfinance-http": {
      "type": "sse",
      "url": "http://localhost:3002/sse"
    }
  }
}
```

## Try It

In VS Code Chat, ask:

- "Get AAPL stock quote"
- "Show me Tesla 6 month chart"
- "What's Microsoft stock price?"

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server shows stopped | Restart via `MCP: List Servers` |
| Port 3002 in use | `netstat -ano \| Select-String ":3002"` then kill process |
| UI shows Loading | Check `chat.mcp.apps.enabled` setting |

## Files

| File | Purpose |
|------|---------|
| [server.py](server.py) | MCP server with SSE transport |
| [AGENTS.md](AGENTS.md) | Architecture documentation |
| [README.md](README.md) | Project overview |
