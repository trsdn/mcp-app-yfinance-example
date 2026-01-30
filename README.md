# YFinance MCP Server with MCP Apps UI

A simple MCP server that provides Yahoo Finance stock data with **rich HTML UI rendering** using the MCP Apps specification.

## Features

- **get_stock_quote** - Get current stock quote with a beautiful card UI showing price, change, mini chart, and key metrics
- **compare_stocks** - Compare multiple stocks side-by-side in a table view

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setup

```bash
# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

## Run the Server

```bash
# With uv
uv run python server.py

# Or directly
python server.py
```

## VS Code Configuration

### Enable MCP Apps
In VS Code Insiders, enable the MCP Apps feature:
```json
{
  "chat.mcp.apps.enabled": true
}
```

### Add to Claude Desktop
Add to your Claude Desktop config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uv",
      "args": ["run", "python", "C:/path/to/mcp-app/server.py"]
    }
  }
}
```

## Example Usage

Ask Claude:
- "Get the stock quote for AAPL"
- "Compare AAPL, MSFT, and GOOGL"
- "What's the current price of Tesla stock?"

## MCP Apps Spec

This server uses the MCP Apps specification to return `structuredContent` with HTML UI:

```python
return {
    "structuredContent": {
        "type": "resource",
        "resource": {
            "uri": "ui://stock-AAPL.html",
            "mimeType": "text/html;profile=mcp-app",
            "text": "<html>...</html>"
        }
    }
}
```

The `mimeType: "text/html;profile=mcp-app"` signals to VS Code that this is an MCP App UI component.
