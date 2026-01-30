"""Test that data is properly embedded in HTML."""
import json
import sys

# Read the server.py file to get the STOCK_CARD_HTML template
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Extract STOCK_CARD_HTML
start = content.find("STOCK_CARD_HTML = '''") + len("STOCK_CARD_HTML = '''")
end = content.find("'''", start)
STOCK_CARD_HTML = content[start:end]

# Simulate having data
test_data = {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "price": 258.28,
    "change": 0.72,
    "changeAmount": 1.84,
    "history": [250, 255, 260, 258, 262, 265, 260, 258],
    "period": "3mo",
    "periodLabel": "3 months",
    "open": 257.50,
    "dayHigh": 259.65,
    "dayLow": 254.41,
    "volumeFormatted": "55.64M",
    "marketCapFormatted": "3.82T",
    "fiftyTwoWeekLow": 169.21,
    "fiftyTwoWeekHigh": 288.62
}

# Do the same replacements as read_resource
data_json = json.dumps(test_data)
html = STOCK_CARD_HTML.replace(
    'let currentData = null;',
    f'let currentData = {data_json};'
).replace(
    'let currentTicker = null;',
    f'let currentTicker = "{test_data.get("ticker", "")}";'
).replace(
    "let currentPeriod = '1mo';",
    f"let currentPeriod = '{test_data.get('period', '1mo')}';"
)

# Write to file for inspection
with open('test_output.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ Wrote test_output.html")
