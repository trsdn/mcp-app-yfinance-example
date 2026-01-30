"""
YFinance MCP Server with MCP Apps UI Support
Implements the MCP Apps spec (SEP-1865) with predeclared UI resources.
"""

import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult, Resource, ResourceContents, TextResourceContents
import yfinance as yf


app = Server("yfinance-mcp")

# Store for dynamic data that will be passed to the UI
_last_stock_data = {}
_last_comparison_data = {}


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


# ============== UI Resource Templates ==============

STOCK_CARD_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
            background: var(--color-background-primary, linear-gradient(135deg, #1e293b 0%, #0f172a 100%));
            color: var(--color-text-primary, #f1f5f9);
            padding: 16px;
            min-height: 200px;
        }
        .card {
            background: var(--color-background-secondary, rgba(30, 41, 59, 0.8));
            border-radius: var(--border-radius-lg, 12px);
            padding: 20px;
            border: 1px solid var(--color-border-primary, rgba(148, 163, 184, 0.1));
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }
        .ticker {
            font-size: 14px;
            color: var(--color-text-secondary, #94a3b8);
            font-weight: 500;
        }
        .name {
            font-size: 18px;
            font-weight: 600;
            margin-top: 4px;
        }
        .price-section {
            text-align: right;
        }
        .price {
            font-size: 28px;
            font-weight: 700;
        }
        .change {
            font-size: 14px;
            margin-top: 4px;
        }
        .change.positive { color: var(--color-text-success, #22c55e); }
        .change.negative { color: var(--color-text-danger, #ef4444); }
        .chart {
            margin: 20px 0;
            height: 100px;
            background: var(--color-background-tertiary, rgba(15, 23, 42, 0.3));
            border-radius: var(--border-radius-md, 8px);
            padding: 8px;
        }
        .chart-label {
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: var(--color-text-tertiary, #64748b);
            margin-top: 4px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 16px;
        }
        .stat {
            text-align: center;
            padding: 8px;
            background: var(--color-background-tertiary, rgba(15, 23, 42, 0.5));
            border-radius: var(--border-radius-md, 8px);
        }
        .stat-label {
            font-size: 11px;
            color: var(--color-text-tertiary, #64748b);
            text-transform: uppercase;
        }
        .stat-value {
            font-size: 14px;
            font-weight: 600;
            margin-top: 4px;
        }
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
            color: var(--color-text-secondary, #94a3b8);
        }
    </style>
</head>
<body>
    <div id="app" class="loading">Loading stock data...</div>
    
    <script>
        // Listen for tool input from host
        window.addEventListener('message', function(event) {
            const data = event.data;
            
            // Handle tool result notification
            if (data.method === 'ui/notifications/tool-result' && data.params?.structuredContent) {
                renderStock(data.params.structuredContent);
            }
            // Handle tool input notification (arguments)
            if (data.method === 'ui/notifications/tool-input') {
                // Tool arguments available - could use for loading state
            }
        });
        
        // Send initialize request
        window.parent.postMessage({
            jsonrpc: "2.0",
            id: 1,
            method: "ui/initialize",
            params: {
                protocolVersion: "2026-01-26",
                appCapabilities: {}
            }
        }, '*');
        
        function renderStock(data) {
            const app = document.getElementById('app');
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.change >= 0 ? '▲' : '▼';
            
            // Build chart SVG
            let chartSvg = '';
            if (data.history && data.history.length >= 2) {
                const prices = data.history;
                const minP = Math.min(...prices) * 0.99;
                const maxP = Math.max(...prices) * 1.01;
                const rangeP = maxP - minP || 1;
                const step = 300 / (prices.length - 1);
                
                const points = prices.map((p, i) => {
                    const x = i * step;
                    const y = 80 - ((p - minP) / rangeP * 70);
                    return `${x.toFixed(1)},${y.toFixed(1)}`;
                }).join(' ');
                
                const areaPoints = points + ' 300,85 0,85';
                const color = data.change >= 0 ? '#22c55e' : '#ef4444';
                
                chartSvg = `
                    <svg width="100%" height="85" viewBox="0 0 300 85" preserveAspectRatio="none">
                        <defs>
                            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" style="stop-color:${color};stop-opacity:0.3"/>
                                <stop offset="100%" style="stop-color:${color};stop-opacity:0.05"/>
                            </linearGradient>
                        </defs>
                        <polygon fill="url(#chartGradient)" points="${areaPoints}"/>
                        <polyline fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="${points}"/>
                    </svg>
                `;
            }
            
            app.className = 'card';
            app.innerHTML = `
                <div class="header">
                    <div>
                        <div class="ticker">${data.ticker}</div>
                        <div class="name">${data.name}</div>
                    </div>
                    <div class="price-section">
                        <div class="price">$${data.price?.toFixed(2) || 'N/A'}</div>
                        <div class="change ${changeClass}">${changeSymbol} $${Math.abs(data.changeAmount || 0).toFixed(2)} (${Math.abs(data.change || 0).toFixed(2)}%)</div>
                    </div>
                </div>
                
                <div class="chart">
                    ${chartSvg}
                    <div class="chart-label">
                        <span>${data.periodLabel || '30 days'} ago</span>
                        <span>Today</span>
                    </div>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-label">Open</div>
                        <div class="stat-value">$${data.open?.toFixed(2) || 'N/A'}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">High</div>
                        <div class="stat-value">$${data.dayHigh?.toFixed(2) || 'N/A'}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Low</div>
                        <div class="stat-value">$${data.dayLow?.toFixed(2) || 'N/A'}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Volume</div>
                        <div class="stat-value">${data.volumeFormatted || 'N/A'}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Market Cap</div>
                        <div class="stat-value">${data.marketCapFormatted || 'N/A'}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">52W Range</div>
                        <div class="stat-value">$${data.fiftyTwoWeekLow?.toFixed(0) || 'N/A'} - $${data.fiftyTwoWeekHigh?.toFixed(0) || 'N/A'}</div>
                    </div>
                </div>
            `;
        }
    </script>
</body>
</html>'''


COMPARISON_HTML = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
            background: var(--color-background-primary, linear-gradient(135deg, #1e293b 0%, #0f172a 100%));
            color: var(--color-text-primary, #f1f5f9);
            padding: 16px;
        }
        h2 {
            margin-bottom: 16px;
            font-size: 18px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--color-background-secondary, rgba(30, 41, 59, 0.8));
            border-radius: var(--border-radius-md, 8px);
            overflow: hidden;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--color-border-primary, rgba(148, 163, 184, 0.1));
        }
        th {
            background: var(--color-background-tertiary, rgba(15, 23, 42, 0.5));
            font-size: 11px;
            text-transform: uppercase;
            color: var(--color-text-tertiary, #64748b);
        }
        tr:hover {
            background: rgba(51, 65, 85, 0.5);
        }
        .positive { color: var(--color-text-success, #22c55e); }
        .negative { color: var(--color-text-danger, #ef4444); }
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
            color: var(--color-text-secondary, #94a3b8);
        }
    </style>
</head>
<body>
    <div id="app" class="loading">Loading comparison...</div>
    
    <script>
        window.addEventListener('message', function(event) {
            const data = event.data;
            if (data.method === 'ui/notifications/tool-result' && data.params?.structuredContent) {
                renderComparison(data.params.structuredContent);
            }
        });
        
        window.parent.postMessage({
            jsonrpc: "2.0",
            id: 1,
            method: "ui/initialize",
            params: { protocolVersion: "2026-01-26", appCapabilities: {} }
        }, '*');
        
        function makeSparkline(history, color) {
            if (!history || history.length < 2) return '—';
            const prices = history.slice(-20);
            const minP = Math.min(...prices) * 0.99;
            const maxP = Math.max(...prices) * 1.01;
            const rangeP = maxP - minP || 1;
            const step = 80 / (prices.length - 1);
            const points = prices.map((p, i) => `${(i * step).toFixed(1)},${(24 - ((p - minP) / rangeP * 20)).toFixed(1)}`).join(' ');
            return `<svg width="80" height="24" viewBox="0 0 80 24"><polyline fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" points="${points}"/></svg>`;
        }
        
        function renderComparison(data) {
            const app = document.getElementById('app');
            const rows = data.stocks.map(s => {
                const changeClass = (s.change || 0) >= 0 ? 'positive' : 'negative';
                const color = (s.change || 0) >= 0 ? '#22c55e' : '#ef4444';
                return `
                    <tr>
                        <td><strong>${s.ticker}</strong><br><span style="color:#64748b;font-size:12px;">${(s.name || '').substring(0, 20)}</span></td>
                        <td style="font-weight:600;">$${s.price?.toFixed(2) || 'N/A'}</td>
                        <td class="${changeClass}">${(s.change || 0).toFixed(2)}%</td>
                        <td>${makeSparkline(s.history, color)}</td>
                        <td>${s.marketCapFormatted || 'N/A'}</td>
                        <td>${s.pe?.toFixed(1) || 'N/A'}</td>
                        <td>${s.dividend ? (s.dividend * 100).toFixed(2) + '%' : 'N/A'}</td>
                    </tr>
                `;
            }).join('');
            
            app.innerHTML = `
                <h2>📊 Stock Comparison</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Stock</th>
                            <th>Price</th>
                            <th>Change</th>
                            <th>${data.trendLabel || 'Trend'}</th>
                            <th>Market Cap</th>
                            <th>P/E</th>
                            <th>Div Yield</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
            app.className = '';
        }
    </script>
</body>
</html>'''


# ============== Resource Handlers ==============

@app.list_resources()
async def list_resources():
    """List available UI resources."""
    return [
        Resource(
            uri="ui://yfinance/stock-card",
            name="Stock Card UI",
            description="Interactive stock quote card with chart",
            mimeType="text/html;profile=mcp-app"
        ),
        Resource(
            uri="ui://yfinance/comparison",
            name="Stock Comparison UI", 
            description="Side-by-side stock comparison table",
            mimeType="text/html;profile=mcp-app"
        )
    ]


@app.read_resource()
async def read_resource(uri: str):
    """Read a UI resource. Returns the HTML content as a string."""
    uri_str = str(uri)  # Convert AnyUrl to string if needed
    import sys
    print(f"[DEBUG] read_resource called with uri: {repr(uri_str)}", file=sys.stderr)
    
    if uri_str == "ui://yfinance/stock-card":
        return STOCK_CARD_HTML
    elif uri_str == "ui://yfinance/comparison":
        return COMPARISON_HTML
    else:
        print(f"[DEBUG] Unknown resource URI: {repr(uri_str)}", file=sys.stderr)
        raise ValueError(f"Unknown resource: {uri_str}")


# ============== HTML Generation Helpers ==============

def generate_stock_html(data):
    """Generate HTML card for stock data (fallback for non-MCP-Apps clients)."""
    change_class = "positive" if data.get("change", 0) >= 0 else "negative"
    change_symbol = "▲" if data.get("change", 0) >= 0 else "▼"
    color = "#22c55e" if data.get("change", 0) >= 0 else "#ef4444"
    
    # Pre-compute formatted values
    price_str = f"${data.get('price', 0):.2f}"
    change_amt_str = f"${abs(data.get('changeAmount', 0)):.2f}"
    change_pct_str = f"{abs(data.get('change', 0)):.2f}%"
    open_str = f"${data.get('open'):.2f}" if data.get('open') else "N/A"
    high_str = f"${data.get('dayHigh'):.2f}" if data.get('dayHigh') else "N/A"
    low_str = f"${data.get('dayLow'):.2f}" if data.get('dayLow') else "N/A"
    low_52w = f"${data.get('fiftyTwoWeekLow'):.0f}" if data.get('fiftyTwoWeekLow') else "N/A"
    high_52w = f"${data.get('fiftyTwoWeekHigh'):.0f}" if data.get('fiftyTwoWeekHigh') else "N/A"
    range_52w = f"{low_52w} - {high_52w}"
    
    # Build chart SVG
    chart_svg = ""
    history = data.get("history", [])
    if len(history) >= 2:
        prices = history
        min_p = min(prices) * 0.99
        max_p = max(prices) * 1.01
        range_p = max_p - min_p or 1
        step = 300 / (len(prices) - 1)
        
        points = " ".join([
            f"{i * step:.1f},{80 - ((p - min_p) / range_p * 70):.1f}"
            for i, p in enumerate(prices)
        ])
        area_points = points + " 300,85 0,85"
        
        chart_svg = f'''
            <svg width="100%" height="85" viewBox="0 0 300 85" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style="stop-color:{color};stop-opacity:0.3"/>
                        <stop offset="100%" style="stop-color:{color};stop-opacity:0.05"/>
                    </linearGradient>
                </defs>
                <polygon fill="url(#chartGradient)" points="{area_points}"/>
                <polyline fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{points}"/>
            </svg>
        '''
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #f1f5f9;
            padding: 16px;
            min-height: 200px;
        }}
        .card {{
            background: rgba(30, 41, 59, 0.8);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }}
        .ticker {{
            font-size: 14px;
            color: #94a3b8;
            font-weight: 500;
        }}
        .name {{
            font-size: 18px;
            font-weight: 600;
            margin-top: 4px;
        }}
        .price-section {{
            text-align: right;
        }}
        .price {{
            font-size: 28px;
            font-weight: 700;
        }}
        .change {{
            font-size: 14px;
            margin-top: 4px;
            color: {color};
        }}
        .chart {{
            margin: 20px 0;
            height: 100px;
            background: rgba(15, 23, 42, 0.3);
            border-radius: 8px;
            padding: 8px;
        }}
        .chart-label {{
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: #64748b;
            margin-top: 4px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 16px;
        }}
        .stat {{
            text-align: center;
            padding: 8px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
        }}
        .stat-label {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
        }}
        .stat-value {{
            font-size: 14px;
            font-weight: 600;
            margin-top: 4px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div>
                <div class="ticker">{data.get("ticker", "N/A")}</div>
                <div class="name">{data.get("name", "N/A")}</div>
            </div>
            <div class="price-section">
                <div class="price">{price_str}</div>
                <div class="change">{change_symbol} {change_amt_str} ({change_pct_str})</div>
            </div>
        </div>
        
        <div class="chart">
            {chart_svg}
            <div class="chart-label">
                <span>{data.get("periodLabel", "1 month")} ago</span>
                <span>Today</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-label">Open</div>
                <div class="stat-value">{open_str}</div>
            </div>
            <div class="stat">
                <div class="stat-label">High</div>
                <div class="stat-value">{high_str}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Low</div>
                <div class="stat-value">{low_str}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Volume</div>
                <div class="stat-value">{data.get("volumeFormatted", "N/A")}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Market Cap</div>
                <div class="stat-value">{data.get("marketCapFormatted", "N/A")}</div>
            </div>
            <div class="stat">
                <div class="stat-label">52W Range</div>
                <div class="stat-value">{range_52w}</div>
            </div>
        </div>
    </div>
</body>
</html>'''


def generate_comparison_html(data):
    """Generate HTML comparison table for multiple stocks (fallback for non-MCP-Apps clients)."""
    rows = ""
    for s in data.get("stocks", []):
        change = s.get("change", 0)
        change_class = "positive" if change >= 0 else "negative"
        color = "#22c55e" if change >= 0 else "#ef4444"
        
        # Pre-compute formatted values
        price_str = f"${s.get('price'):.2f}" if s.get('price') else "N/A"
        pe_str = f"{s.get('pe'):.1f}" if s.get('pe') else "N/A"
        div_str = f"{(s.get('dividend', 0) or 0) * 100:.2f}%"
        
        # Generate mini sparkline
        sparkline = "—"
        history = s.get("history", [])
        if len(history) >= 2:
            prices = history[-20:]
            min_p = min(prices) * 0.99
            max_p = max(prices) * 1.01
            range_p = max_p - min_p or 1
            step = 80 / (len(prices) - 1)
            points = " ".join([f"{i * step:.1f},{24 - ((p - min_p) / range_p * 20):.1f}" for i, p in enumerate(prices)])
            sparkline = f'<svg width="80" height="24" viewBox="0 0 80 24"><polyline fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" points="{points}"/></svg>'
        
        rows += f'''
            <tr>
                <td><strong>{s.get("ticker", "N/A")}</strong><br><span style="color:#64748b;font-size:12px;">{(s.get("name", "")[:20])}</span></td>
                <td style="font-weight:600;">{price_str}</td>
                <td class="{change_class}">{change:.2f}%</td>
                <td>{sparkline}</td>
                <td>{s.get("marketCapFormatted", "N/A")}</td>
                <td>{pe_str}</td>
                <td>{div_str}</td>
            </tr>
        '''
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #f1f5f9;
            padding: 16px;
        }}
        h2 {{
            margin-bottom: 16px;
            font-size: 18px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }}
        th {{
            background: rgba(15, 23, 42, 0.5);
            font-size: 11px;
            text-transform: uppercase;
            color: #64748b;
        }}
        tr:hover {{
            background: rgba(51, 65, 85, 0.5);
        }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
    </style>
</head>
<body>
    <h2>📊 Stock Comparison</h2>
    <table>
        <thead>
            <tr>
                <th>Stock</th>
                <th>Price</th>
                <th>Change</th>
                <th>{data.get("trendLabel", "Trend")}</th>
                <th>Market Cap</th>
                <th>P/E</th>
                <th>Div Yield</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
</body>
</html>'''


# ============== Tool Handlers ==============

@app.list_tools()
async def list_tools():
    """List available tools with UI metadata."""
    return [
        Tool(
            name="get_stock_quote",
            description="Get current stock quote with price, change, and key metrics. Returns a rich UI card with chart.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
                    },
                    "period": {
                        "type": "string",
                        "description": "Chart time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                        "default": "1mo"
                    }
                },
                "required": ["ticker"]
            },
            # MCP Apps metadata - link to UI resource
            _meta={
                "ui": {
                    "resourceUri": "ui://yfinance/stock-card"
                }
            }
        ),
        Tool(
            name="compare_stocks",
            description="Compare multiple stocks side by side with a rich UI comparison table and sparkline charts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock ticker symbols to compare (e.g., ['AAPL', 'MSFT', 'GOOGL'])"
                    },
                    "period": {
                        "type": "string",
                        "description": "Chart time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                        "default": "1mo"
                    }
                },
                "required": ["tickers"]
            },
            _meta={
                "ui": {
                    "resourceUri": "ui://yfinance/comparison"
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls - return structured data for the UI."""
    
    period_labels = {
        "1d": "Today", "5d": "5 days", "1mo": "1 month", "3mo": "3 months",
        "6mo": "6 months", "1y": "1 year", "2y": "2 years", "5y": "5 years",
        "10y": "10 years", "ytd": "YTD", "max": "All time"
    }
    
    if name == "get_stock_quote":
        ticker = arguments.get("ticker", "").upper()
        period = arguments.get("period", "1mo")
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get history for chart
            hist = stock.history(period=period)
            hist_close = hist["Close"].tolist() if not hist.empty else []
            
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            prev_close = info.get("previousClose", 0)
            change_amount = (price - prev_close) if price and prev_close else 0
            change_pct = (change_amount / prev_close * 100) if prev_close else 0
            
            # Return structured data that the UI will render
            structured_data = {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "price": price,
                "change": change_pct,
                "changeAmount": change_amount,
                "open": info.get("open"),
                "dayHigh": info.get("dayHigh"),
                "dayLow": info.get("dayLow"),
                "volume": info.get("volume"),
                "volumeFormatted": format_number(info.get("volume", 0)),
                "marketCap": info.get("marketCap"),
                "marketCapFormatted": format_number(info.get("marketCap", 0)),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "history": hist_close,
                "period": period,
                "periodLabel": period_labels.get(period, period)
            }
            
            # Return structuredContent - VS Code MCP Apps will fetch the UI from the tool's _meta.ui.resourceUri
            # and post this data to it via postMessage
            return CallToolResult(
                content=[TextContent(type="text", text=f"{info.get('longName', ticker)} ({ticker}): ${price:.2f} ({change_pct:+.2f}%)")],
                structuredContent=structured_data
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error fetching data for {ticker}: {str(e)}")],
                isError=True
            )
    
    elif name == "compare_stocks":
        tickers = [t.upper() for t in arguments.get("tickers", [])]
        period = arguments.get("period", "1mo")
        
        if not tickers:
            return CallToolResult(
                content=[TextContent(type="text", text="Please provide at least one ticker symbol.")],
                isError=True
            )
        
        try:
            stocks_data = []
            for ticker in tickers[:5]:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                hist = stock.history(period=period)
                hist_close = hist["Close"].tolist() if not hist.empty else []
                
                stocks_data.append({
                    "ticker": ticker,
                    "name": info.get("longName", ticker),
                    "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "change": info.get("regularMarketChangePercent", 0),
                    "marketCap": info.get("marketCap", 0),
                    "marketCapFormatted": format_number(info.get("marketCap", 0)),
                    "pe": info.get("trailingPE"),
                    "dividend": info.get("dividendYield", 0),
                    "history": hist_close
                })
            
            trend_labels = {
                "1d": "1D", "5d": "5D", "1mo": "1M", "3mo": "3M",
                "6mo": "6M", "1y": "1Y", "2y": "2Y", "5y": "5Y",
                "10y": "10Y", "ytd": "YTD", "max": "All"
            }
            
            structured_data = {
                "stocks": stocks_data,
                "period": period,
                "trendLabel": trend_labels.get(period, period) + " Trend"
            }
            
            # Return structuredContent - VS Code MCP Apps will fetch the UI from the tool's _meta.ui.resourceUri
            tickers_str = ", ".join([s["ticker"] for s in stocks_data])
            return CallToolResult(
                content=[TextContent(type="text", text=f"Comparison: {tickers_str}")],
                structuredContent=structured_data
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error comparing stocks: {str(e)}")],
                isError=True
            )
    
    return CallToolResult(
        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
        isError=True
    )


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
