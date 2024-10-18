from fridonai_core.plugins.utilities.mock import BaseMockUtility, RemoteMockUtility


class CoinPriceChartSimilaritySearchMockUtility(RemoteMockUtility):
    coin_prices = {
        "sol": {"prices": [1, 2], "score": 10},
        "eth": {"prices": [1, 2], "score": 10},
    }

    async def arun(
        self, coin_name: str, start_date: str | None = None, *args, **kwargs
    ) -> dict | str:
        if coin_name not in self.coin_prices:
            return "We don't support this coin yet."
        return {"data": self.coin_prices[coin_name]}



class CoinTechnicalIndicatorsSearchMockUtility(BaseMockUtility):
    async def arun(self, *args, **kwargs) -> list:
        return "[MACD, RSI]"