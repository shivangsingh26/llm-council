"""
Tests for Finance API tool.

Tests real Yahoo Finance data access.
"""

import asyncio
from src.tools.finance_api import FinanceAPI, get_stock_data, get_market_data


async def test_stock_price():
    """Test getting stock price data."""
    api = FinanceAPI()

    print("\n📊 Testing Stock Price (Apple)...")
    result = await api.get_stock_price("AAPL")

    assert result["success"] is True
    assert result["symbol"] == "AAPL"
    assert result["current_price"] is not None
    assert "Apple" in result["company_name"]

    print(f"✅ {result['company_name']}: ${result['current_price']}")
    print(f"   Change: ${result['change']} ({result['change_percent']:+.2f}%)")


async def test_company_info():
    """Test getting company information."""
    api = FinanceAPI()

    print("\n🏢 Testing Company Info (Microsoft)...")
    result = await api.get_company_info("MSFT")

    assert result["success"] is True
    assert result["symbol"] == "MSFT"
    assert result["company_name"] is not None
    assert result["sector"] is not None

    print(f"✅ {result['company_name']}")
    print(f"   Sector: {result['sector']}")
    print(f"   Industry: {result['industry']}")


async def test_company_news():
    """Test getting company news."""
    api = FinanceAPI()

    print("\n📰 Testing Company News (Tesla)...")
    result = await api.get_company_news("TSLA", limit=3)

    assert result["success"] is True
    assert result["symbol"] == "TSLA"
    assert len(result["articles"]) > 0

    print(f"✅ Found {result['news_count']} articles")
    for article in result["articles"][:2]:
        title = article.get('title') or 'No title'
        print(f"   • {title[:60]}...")


async def test_market_summary():
    """Test getting market indices."""
    api = FinanceAPI()

    print("\n📈 Testing Market Summary...")
    result = await api.get_market_summary()

    assert result["success"] is True
    assert "indices" in result
    assert "^GSPC" in result["indices"]  # S&P 500
    assert "^DJI" in result["indices"]   # Dow Jones
    assert "^IXIC" in result["indices"]  # NASDAQ

    print("✅ Market Indices:")
    for symbol, data in result["indices"].items():
        print(f"   {data['name']}: {data['price']} ({data['change_percent']:+.2f}%)")


async def test_historical_data():
    """Test getting historical data."""
    api = FinanceAPI()

    print("\n📉 Testing Historical Data (Google - 1 month)...")
    result = await api.get_historical_data("GOOGL", period="1mo")

    assert result["success"] is True
    assert result["symbol"] == "GOOGL"
    assert len(result["data"]) > 0
    assert "summary" in result

    print(f"✅ Retrieved {result['data_points_count']} data points")
    print(f"   Start: ${result['summary']['start_price']}")
    print(f"   End: ${result['summary']['end_price']}")
    print(f"   Change: {result['summary']['total_change_percent']:+.2f}%")


async def test_formatting():
    """Test prompt formatting."""
    api = FinanceAPI()

    print("\n🎨 Testing Prompt Formatting...")
    result = await api.get_stock_price("AAPL")

    formatted = api.format_for_prompt(result)
    assert "Apple" in formatted
    assert "$" in formatted
    assert "%" in formatted

    print("✅ Formatted output:")
    print(formatted[:200] + "...")


async def test_convenience_functions():
    """Test convenience functions."""
    print("\n⚡ Testing Convenience Functions...")

    # Test stock data function
    stock_data = await get_stock_data("TSLA")
    assert stock_data["success"] is True
    print(f"✅ get_stock_data: {stock_data['symbol']} @ ${stock_data['current_price']}")

    # Test market data function
    market_data = await get_market_data()
    assert market_data["success"] is True
    print(f"✅ get_market_data: {len(market_data['indices'])} indices")


async def test_invalid_symbol():
    """Test error handling for invalid symbol."""
    api = FinanceAPI()

    print("\n❌ Testing Error Handling (Invalid Symbol)...")
    result = await api.get_stock_price("INVALID_SYMBOL_XYZ")

    # Should handle gracefully
    print(f"✅ Handled error: {result.get('error', 'No data')[:50]}")


async def main():
    """Run all tests."""
    print("🚀 Testing Finance API with Yahoo Finance")
    print("=" * 60)

    await test_stock_price()
    await test_company_info()
    await test_company_news()
    await test_market_summary()
    await test_historical_data()
    await test_formatting()
    await test_convenience_functions()
    await test_invalid_symbol()

    print("\n" + "=" * 60)
    print("🎉 All Finance API tests passed!")
    print("\n💡 The Finance API is working with real-time data from Yahoo Finance!")


if __name__ == "__main__":
    asyncio.run(main())
