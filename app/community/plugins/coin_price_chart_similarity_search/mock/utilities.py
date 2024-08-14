from app.core.plugins.utilities.mock import BlockchainMockUtility, RemoteMockUtility


class CoinPriceChartSimilaritySearchMockUtility(RemoteMockUtility):
    async def arun(
            self,
            coin_name: str,
            start_date: str | None = None,
            *args,
            **kwargs
    ) -> dict:
        return {"data": {"sol": {"prices": [1, 2], "score": 10}}}


