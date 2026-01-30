# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-30

### Added
- Initial release of MCP Apps Stock Server example
- `get_stock_quote` tool with interactive chart UI
- SSE transport on port 3002
- Period switching (1D, 5D, 1M, 3M, 6M, 1Y, 5Y)
- postMessage handshake for MCP Apps integration
- Architecture Decision Records (ADRs)
- VS Code MCP configuration

### Technical
- Python MCP server with Starlette/uvicorn
- yfinance for stock data
- Canvas-based chart rendering (no external libraries)
- structuredContent for UI data passing
