"""
YFinance MCP Server with HTTP/SSE transport for MCP Apps
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult, Resource
from mcp.server.sse import SseServerTransport
import yfinance as yf
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
import uvicorn
import sys


app_server = Server("yfinance-http")


def format_number(num):
    """Format large numbers with K, M, B suffixes."""
    if not num or not isinstance(num, (int, float)):
        return "N/A"
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    if num >= 1_000:
        return f"{num / 1_000:.2f}K"
    return str(num)


# Full stock card HTML with postMessage handshake and period switcher
STOCK_CARD_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #e2e8f0; padding: 16px; min-height: 200px; }
.loading { display: flex; align-items: center; justify-content: center; height: 150px; color: #64748b; }
.card { display: none; }
.header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.ticker { font-size: 24px; font-weight: 700; color: #f8fafc; }
.name { font-size: 12px; color: #64748b; margin-top: 2px; }
.price { font-size: 28px; font-weight: 700; text-align: right; }
.change { font-size: 14px; margin-top: 4px; }
.positive { color: #22c55e; }
.negative { color: #ef4444; }
.periods { display: flex; gap: 4px; margin-bottom: 12px; }
.period-btn { background: #1e293b; border: none; color: #94a3b8; padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.15s; }
.period-btn:hover { background: #334155; color: #e2e8f0; }
.period-btn.active { background: #3b82f6; color: #fff; }
.period-btn:disabled { opacity: 0.5; cursor: wait; }
.chart-container { height: 120px; margin: 12px 0; position: relative; }
canvas { width: 100%; height: 100%; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding-top: 12px; border-top: 1px solid #1e293b; }
.stat { text-align: center; }
.stat-label { font-size: 10px; color: #64748b; text-transform: uppercase; }
.stat-value { font-size: 14px; font-weight: 600; margin-top: 2px; }
</style>
</head>
<body>
<div id="loading" class="loading">Waiting for data...</div>
<div id="card" class="card">
  <div class="header">
    <div>
      <div id="ticker" class="ticker"></div>
      <div id="name" class="name"></div>
    </div>
    <div>
      <div id="price" class="price"></div>
      <div id="change" class="change"></div>
    </div>
  </div>
  <div class="periods">
    <button class="period-btn" data-period="1d">1D</button>
    <button class="period-btn" data-period="5d">5D</button>
    <button class="period-btn" data-period="1mo">1M</button>
    <button class="period-btn" data-period="3mo">3M</button>
    <button class="period-btn" data-period="6mo">6M</button>
    <button class="period-btn" data-period="1y">1Y</button>
    <button class="period-btn" data-period="5y">5Y</button>
  </div>
  <div class="chart-container">
    <canvas id="chart"></canvas>
  </div>
  <div class="stats">
    <div class="stat"><div class="stat-label">Volume</div><div id="volume" class="stat-value"></div></div>
    <div class="stat"><div class="stat-label">Market Cap</div><div id="mcap" class="stat-value"></div></div>
    <div class="stat"><div class="stat-label">52W Range</div><div id="range" class="stat-value"></div></div>
  </div>
</div>
<script>
const pending = new Map();
let nextId = 1;
let currentTicker = '';
let currentPeriod = '';

function request(method, params) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    window.parent.postMessage({ jsonrpc: '2.0', id, method, params }, '*');
  });
}

function updatePeriodButtons(activePeriod) {
  document.querySelectorAll('.period-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.period === activePeriod);
    btn.disabled = false;
  });
}

function switchPeriod(period) {
  if (!currentTicker || period === currentPeriod) return;
  document.querySelectorAll('.period-btn').forEach(btn => btn.disabled = true);
  request('tools/call', {
    name: 'get_stock_quote',
    arguments: { ticker: currentTicker, period: period }
  }).then(result => {
    if (result && result.structuredContent) {
      render(result.structuredContent);
    }
  }).catch(() => {
    updatePeriodButtons(currentPeriod);
  });
}

document.querySelectorAll('.period-btn').forEach(btn => {
  btn.addEventListener('click', () => switchPeriod(btn.dataset.period));
});

function renderChart(canvas, history, isPositive) {
  if (!history || history.length < 2) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);
  
  const w = rect.width, h = rect.height;
  const min = Math.min(...history), max = Math.max(...history);
  const range = max - min || 1;
  const pad = 4;
  
  ctx.beginPath();
  ctx.strokeStyle = isPositive ? '#22c55e' : '#ef4444';
  ctx.lineWidth = 2;
  ctx.lineJoin = 'round';
  
  history.forEach((val, i) => {
    const x = (i / (history.length - 1)) * w;
    const y = h - pad - ((val - min) / range) * (h - pad * 2);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();
  
  // Gradient fill
  const gradient = ctx.createLinearGradient(0, 0, 0, h);
  gradient.addColorStop(0, isPositive ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)');
  gradient.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.lineTo(w, h);
  ctx.lineTo(0, h);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();
}

function render(data) {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('card').style.display = 'block';
  
  currentTicker = data.ticker;
  currentPeriod = data.period;
  
  const isPositive = data.change >= 0;
  const sign = isPositive ? '+' : '';
  
  document.getElementById('ticker').textContent = data.ticker;
  document.getElementById('name').textContent = data.name || '';
  document.getElementById('price').textContent = '$' + (data.price || 0).toFixed(2);
  
  const changeEl = document.getElementById('change');
  changeEl.textContent = sign + (data.change || 0).toFixed(2) + '% (' + sign + '$' + (data.changeAmount || 0).toFixed(2) + ')';
  changeEl.className = 'change ' + (isPositive ? 'positive' : 'negative');
  document.getElementById('price').className = 'price ' + (isPositive ? 'positive' : 'negative');
  
  document.getElementById('volume').textContent = data.volumeFormatted || 'N/A';
  document.getElementById('mcap').textContent = data.marketCapFormatted || 'N/A';
  document.getElementById('range').textContent = (data.fiftyTwoWeekLow ? '$' + data.fiftyTwoWeekLow.toFixed(0) : '?') + ' - ' + (data.fiftyTwoWeekHigh ? '$' + data.fiftyTwoWeekHigh.toFixed(0) : '?');
  
  updatePeriodButtons(data.period);
  renderChart(document.getElementById('chart'), data.history, isPositive);
}

window.addEventListener('message', (e) => {
  const msg = e.data;
  if (!msg || !msg.jsonrpc) return;
  
  // Handle responses to our requests
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(msg.error) : resolve(msg.result);
    return;
  }
  
  // Handle notifications from host
  if (msg.method === 'ui/notifications/tool-result') {
    const sc = msg.params && msg.params.structuredContent;
    if (sc) render(sc);
  }
  if (msg.method === 'ui/notifications/tool-input') {
    // Could use input args if needed
  }
});

// Initialize handshake
request('ui/initialize', { protocolVersion: '2025-11-21' })
  .then(() => {
    window.parent.postMessage({ jsonrpc: '2.0', method: 'ui/notifications/initialized' }, '*');
  })
  .catch(() => {
    document.getElementById('loading').textContent = 'Init failed';
  });
''' + '</scr' + 'ipt>' + '''
</body>
</html>'''


@app_server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="ui://yfinance/stock-card",
            name="Stock Card",
            description="Stock quote card",
            mimeType="text/html;profile=mcp-app"
        )
    ]


@app_server.read_resource()
async def read_resource(uri: str) -> str:
    """Return resource content as string. MIME type is set in list_resources."""
    print(f"[HTTP] read_resource: {uri}", file=sys.stderr)
    if str(uri) == "ui://yfinance/stock-card":
        return STOCK_CARD_HTML
    raise ValueError(f"Unknown resource: {uri}")


@app_server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_stock_quote",
            description="Get stock quote with interactive UI",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "period": {"type": "string", "default": "1mo"}
                },
                "required": ["ticker"]
            },
            _meta={"ui": {"resourceUri": "ui://yfinance/stock-card"}}
        )
    ]


@app_server.call_tool()
async def call_tool(name: str, arguments: dict):
    print(f"[HTTP] call_tool: {name} with {arguments}", file=sys.stderr)

    period_labels = {
        "1d": "Today", "5d": "5 days", "1mo": "1 month", "3mo": "3 months",
        "6mo": "6 months", "1y": "1 year", "2y": "2 years", "5y": "5 years"
    }

    if name == "get_stock_quote":
        ticker = arguments.get("ticker", "").upper()
        period = arguments.get("period", "1mo")

        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            
            # Get history for chart
            period_intervals = {"1d": "5m", "5d": "15m"}
            interval = period_intervals.get(period, "1d")
            hist = stock.history(period=period, interval=interval)
            hist_close = hist["Close"].tolist() if not hist.empty else []
            
            # Calculate period change
            if hist_close and len(hist_close) >= 2:
                start_price = hist_close[0]
                change_amount = price - start_price
                change_pct = (change_amount / start_price * 100) if start_price else 0
            else:
                prev_close = info.get("previousClose", 0)
                change_amount = (price - prev_close) if price and prev_close else 0
                change_pct = (change_amount / prev_close * 100) if prev_close else 0

            data = {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "price": price,
                "change": change_pct,
                "changeAmount": change_amount,
                "period": period,
                "periodLabel": period_labels.get(period, period),
                "history": hist_close,
                "volume": info.get("volume"),
                "volumeFormatted": format_number(info.get("volume", 0)),
                "marketCap": info.get("marketCap"),
                "marketCapFormatted": format_number(info.get("marketCap", 0)),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "open": info.get("open"),
                "dayHigh": info.get("dayHigh"),
                "dayLow": info.get("dayLow")
            }

            print(f"[HTTP] Returning data with {len(hist_close)} history points", file=sys.stderr)
            return CallToolResult(
                content=[TextContent(type="text", text=f"{ticker}: ${price:.2f} ({change_pct:+.2f}% over {period_labels.get(period, period)})")],
                structuredContent=data
            )
        except Exception as e:
            print(f"[HTTP] Error: {e}", file=sys.stderr)
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {e}")],
                isError=True
            )

    return CallToolResult(
        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
        isError=True
    )


# Create a single SSE transport instance (singleton)
sse_transport = SseServerTransport("/sse")


async def handle_sse(request: Request):
    """Handle SSE endpoint - GET for connection, POST for messages"""
    if request.method == "POST":
        print(f"[HTTP] SSE POST request", file=sys.stderr)
        await sse_transport.handle_post_message(request.scope, request.receive, request._send)
        from starlette.responses import Response
        return Response(status_code=202)
    else:
        print(f"[HTTP] SSE GET request", file=sys.stderr)
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await app_server.run(
                read_stream,
                write_stream,
                app_server.create_initialization_options()
            )
        from starlette.responses import Response
        return Response()


async def health_check(request: Request):
    """Health check endpoint to prevent connection drops"""
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok"})


starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET", "POST"]),
        Route("/health", endpoint=health_check, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    print("[HTTP] Starting MCP server on http://127.0.0.1:3002", file=sys.stderr)
    print("[HTTP] SSE endpoint: http://127.0.0.1:3002/sse", file=sys.stderr)
    uvicorn.run(
        starlette_app, 
        host="127.0.0.1", 
        port=3002, 
        log_level="info",
        timeout_keep_alive=120  # Keep connections alive longer
    )
