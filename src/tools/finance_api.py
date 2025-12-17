"""
Finance API tool using Yahoo Finance.

Provides real-time financial data:
- Stock prices and quotes
- Company information
- Market indices
- Historical data
- Company news

All data is FREE via yfinance library!
"""

import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class FinanceAPI:
    """
    Yahoo Finance API wrapper for real-time financial data.

    Examples:
        >>> api = FinanceAPI()
        >>> price = await api.get_stock_price("AAPL")
        >>> print(f"Apple: ${price['current_price']}")
    """

    # Major market indices
    MARKET_INDICES = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "NASDAQ",
        "^RUT": "Russell 2000",
        "^VIX": "VIX (Volatility Index)"
    }

    async def get_stock_price(self, symbol: str) -> Dict:
        """
        Get current stock price and key metrics.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "GOOGL")

        Returns:
            Dict with current price, change, volume, and key metrics

        Example:
            >>> price_data = await api.get_stock_price("TSLA")
            >>> print(f"Price: ${price_data['current_price']}")
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Get current price (try multiple fields as API can vary)
            current_price = (
                info.get("currentPrice") or
                info.get("regularMarketPrice") or
                info.get("previousClose")
            )

            # Calculate changes
            previous_close = info.get("previousClose", 0)
            change = current_price - previous_close if current_price and previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0

            return {
                "success": True,
                "symbol": symbol.upper(),
                "company_name": info.get("longName", symbol),
                "current_price": round(current_price, 2) if current_price else None,
                "previous_close": round(previous_close, 2) if previous_close else None,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange"),
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "symbol": symbol.upper(),
                "error": f"Failed to fetch data: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }

    async def get_company_info(self, symbol: str) -> Dict:
        """
        Get detailed company information.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with company details, sector, industry, description
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "success": True,
                "symbol": symbol.upper(),
                "company_name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary"),
                "website": info.get("website"),
                "employees": info.get("fullTimeEmployees"),
                "city": info.get("city"),
                "state": info.get("state"),
                "country": info.get("country"),
                "ceo": info.get("companyOfficers", [{}])[0].get("name") if info.get("companyOfficers") else None,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "symbol": symbol.upper(),
                "error": f"Failed to fetch company info: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }

    async def get_company_news(self, symbol: str, limit: int = 5) -> Dict:
        """
        Get recent news for a company.

        Args:
            symbol: Stock ticker symbol
            limit: Number of news articles to return (default: 5)

        Returns:
            Dict with news articles
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news[:limit] if ticker.news else []

            articles = []
            for article in news:
                articles.append({
                    "title": article.get("title"),
                    "publisher": article.get("publisher"),
                    "link": article.get("link"),
                    "published": datetime.fromtimestamp(
                        article.get("providerPublishTime", 0)
                    ).isoformat() if article.get("providerPublishTime") else None,
                    "type": article.get("type")
                })

            return {
                "success": True,
                "symbol": symbol.upper(),
                "company_name": ticker.info.get("longName", symbol),
                "news_count": len(articles),
                "articles": articles,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "symbol": symbol.upper(),
                "error": f"Failed to fetch news: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }

    async def get_market_summary(self) -> Dict:
        """
        Get summary of major market indices.

        Returns:
            Dict with S&P 500, Dow Jones, NASDAQ performance
        """
        try:
            summary = {}

            for symbol, name in self.MARKET_INDICES.items():
                ticker = yf.Ticker(symbol)
                info = ticker.info

                current_price = info.get("regularMarketPrice") or info.get("previousClose")
                previous_close = info.get("previousClose", 0)
                change_percent = (
                    info.get("regularMarketChangePercent") or
                    ((current_price - previous_close) / previous_close * 100 if previous_close else 0)
                )

                summary[symbol] = {
                    "name": name,
                    "price": round(current_price, 2) if current_price else None,
                    "change_percent": round(change_percent, 2),
                    "day_high": info.get("dayHigh"),
                    "day_low": info.get("dayLow")
                }

            return {
                "success": True,
                "indices": summary,
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch market summary: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Dict:
        """
        Get historical price data.

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            Dict with historical data points
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                return {
                    "success": False,
                    "symbol": symbol.upper(),
                    "error": "No historical data available",
                    "last_updated": datetime.now().isoformat()
                }

            # Convert to list of dicts
            data_points = []
            for date, row in hist.iterrows():
                data_points.append({
                    "date": date.isoformat(),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume'])
                })

            # Calculate summary statistics
            latest = data_points[-1]
            earliest = data_points[0]
            total_change = latest['close'] - earliest['close']
            total_change_percent = (total_change / earliest['close'] * 100) if earliest['close'] else 0

            return {
                "success": True,
                "symbol": symbol.upper(),
                "period": period,
                "interval": interval,
                "data_points_count": len(data_points),
                "data": data_points,
                "summary": {
                    "start_price": earliest['close'],
                    "end_price": latest['close'],
                    "total_change": round(total_change, 2),
                    "total_change_percent": round(total_change_percent, 2),
                    "highest": round(max(d['high'] for d in data_points), 2),
                    "lowest": round(min(d['low'] for d in data_points), 2),
                    "avg_volume": int(sum(d['volume'] for d in data_points) / len(data_points))
                },
                "last_updated": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "symbol": symbol.upper(),
                "error": f"Failed to fetch historical data: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }

    def format_for_prompt(self, data: Dict) -> str:
        """
        Format API response for inclusion in LLM prompt.

        Args:
            data: Response from any Finance API method

        Returns:
            Formatted string for prompt context
        """
        if not data.get("success"):
            return f"⚠️ Error fetching data: {data.get('error')}"

        # Format based on data type
        if "current_price" in data:
            # Stock price data
            return f"""📊 **{data['company_name']} ({data['symbol']})**
Current Price: ${data['current_price']} {data['currency']}
Change: ${data['change']} ({data['change_percent']:+.2f}%)
Day Range: ${data['day_low']} - ${data['day_high']}
Volume: {data['volume']:,}
Market Cap: ${data['market_cap']:,}
P/E Ratio: {data['pe_ratio']:.2f}
52-Week Range: ${data['52_week_low']} - ${data['52_week_high']}

Last Updated: {data['last_updated']}"""

        elif "articles" in data:
            # News data
            news_items = "\n".join([
                f"• {article['title']} ({article['publisher']}) - {article['link']}"
                for article in data['articles'][:3]
            ])
            return f"""📰 **Recent News for {data['company_name']}**\n{news_items}"""

        elif "indices" in data:
            # Market summary
            indices_text = "\n".join([
                f"• {idx['name']}: {idx['price']} ({idx['change_percent']:+.2f}%)"
                for idx in data['indices'].values()
            ])
            return f"""📈 **Market Summary**\n{indices_text}\n\nLast Updated: {data['last_updated']}"""

        elif "data_points_count" in data:
            # Historical data
            summary = data['summary']
            return f"""📊 **{data['symbol']} - {data['period']} Historical Data**
Start: ${summary['start_price']} → End: ${summary['end_price']}
Change: ${summary['total_change']} ({summary['total_change_percent']:+.2f}%)
High/Low: ${summary['highest']} / ${summary['lowest']}
Avg Volume: {summary['avg_volume']:,}
Data Points: {data['data_points_count']}"""

        return str(data)


# Convenience functions
async def get_stock_data(symbol: str) -> Dict:
    """Quick function to get stock data."""
    api = FinanceAPI()
    return await api.get_stock_price(symbol)


async def get_market_data() -> Dict:
    """Quick function to get market summary."""
    api = FinanceAPI()
    return await api.get_market_summary()
