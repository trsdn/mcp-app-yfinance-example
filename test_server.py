"""Simple test script to verify the MCP server works."""

import asyncio
import json
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def test_server():
    """Test the yfinance MCP server."""
    
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            print("✅ Server initialized successfully!\n")
            
            # List resources (MCP Apps)
            try:
                resources = await session.list_resources()
                print("📦 Available UI Resources:")
                for res in resources.resources:
                    print(f"   - {res.uri}: {res.name} ({res.mimeType})")
                print()
                
                # Test reading a resource
                print("📖 Testing read_resource for ui://yfinance/stock-card...")
                try:
                    resource_content = await session.read_resource("ui://yfinance/stock-card")
                    print(f"   ✅ Resource read successfully!")
                    print(f"   Content length: {len(resource_content.contents[0].text)} chars")
                except Exception as e:
                    print(f"   ❌ Failed to read resource: {e}")
                print()
            except Exception as e:
                print(f"⚠️  Resources not available: {e}\n")
            
            # List tools
            tools = await session.list_tools()
            print("📋 Available tools:")
            for tool in tools.tools:
                meta = getattr(tool, 'meta', None) or {}
                ui_info = meta.get('ui', {}).get('resourceUri', '')
                meta_info = f" [UI: {ui_info}]" if ui_info else ""
                print(f"   - {tool.name}: {tool.description[:50]}...{meta_info}")
            print()
            
            # Test get_stock_quote
            print("🔍 Testing get_stock_quote for AAPL...")
            result = await session.call_tool("get_stock_quote", {"ticker": "AAPL"})
            
            if result.structuredContent:
                print("✅ Got structuredContent (MCP Apps data)!")
                print(f"   Ticker: {result.structuredContent.get('ticker')}")
                print(f"   Price: ${result.structuredContent.get('price', 0):.2f}")
                print(f"   Change: {result.structuredContent.get('change', 0):.2f}%")
                print(f"   History points: {len(result.structuredContent.get('history', []))}")
            
            if result.content:
                print(f"   Text content type: {getattr(result.content[0], 'mimeType', 'text/plain')}")
                # Save HTML to file for viewing
                html_content = result.content[0].text
                if html_content.startswith('<!DOCTYPE html>'):
                    with open('stock_output.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print("   📄 Saved HTML to stock_output.html")
                else:
                    print(f"   Text fallback: {html_content[:60]}...")
            
            print()
            
            # Test compare_stocks
            print("🔍 Testing compare_stocks for AAPL, MSFT, GOOGL...")
            result = await session.call_tool("compare_stocks", {"tickers": ["AAPL", "MSFT", "GOOGL"]})
            
            if result.structuredContent:
                print("✅ Got structuredContent (MCP Apps data)!")
                stocks = result.structuredContent.get('stocks', [])
                print(f"   Stocks: {len(stocks)}")
                for s in stocks:
                    print(f"   - {s.get('ticker')}: ${s.get('price', 0):.2f}")


if __name__ == "__main__":
    asyncio.run(test_server())
