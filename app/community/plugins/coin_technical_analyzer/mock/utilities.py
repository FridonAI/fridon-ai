from app.core.plugins.utilities.mock import LLMMockUtility


class CoinTechnicalAnalyzerMockUtility(LLMMockUtility):
    coin_analysis = {
        "sol": "Looks very bullish",
        "bonk": "You've to definitely buy it",
    }
    
    async def arun(
            self,
            coin_name: str,
            *args,
            **kwargs
    ) -> str:
        if coin_name not in self.coin_analysis:
            return "We don't support this coin yet."
        return self.coin_analysis[coin_name]
