from app.core.plugins.utilities.mock import LLMMockUtility


class CoinTechnicalAnalyzerMockUtility(LLMMockUtility):
    async def arun(
            self,
            coin_name: str,
            *args,
            **kwargs
    ) -> str:
        return f"{coin_name} looks very bullish."
