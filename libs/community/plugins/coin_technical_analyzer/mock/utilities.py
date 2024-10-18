from fridonai_core.plugins.utilities.mock import BaseMockUtility, LLMMockUtility


class CoinTechnicalAnalyzerMockUtility(LLMMockUtility):
    coin_analysis = {
        "sol": {
            "type": "coin-technical-analyzer",
            "source": "s3",
            "extension": "json",
            "id": "4f916770",
            "name": "coin-technical-analyzer",
            "path": "tool_responses/coin-technical-analyzer/4f916770.json",
            "url": "https://data.fridon.ai/tool_responses/coin-technical-analyzer/4f916770.json"
        },
        "btc": {
            "type": "coin-technical-analyzer",
            "source": "s3",
            "extension": "json",
            "id": "4f916770",
            "name": "coin-technical-analyzer",
            "path": "tool_responses/coin-technical-analyzer/4f916770.json",
            "url": "https://data.fridon.ai/tool_responses/coin-technical-analyzer/4f916770.json"
        }
    }

    async def arun(self, coin_name: str, *args, **kwargs) -> str:
        if coin_name not in self.coin_analysis:
            return "We don't support this coin yet."
        return self.coin_analysis[coin_name]


class CoinTechnicalIndicatorsListMockUtility(BaseMockUtility):
    async def arun(self, *args, **kwargs) -> list:
        return "MACD, RSI"
    

class CoinChartPlotterMockUtility(BaseMockUtility):
    coin_plotter = {
        "sol": {
            "type": "coin-chart-plotter",
            "source": "s3",
            "extension": "json",
            "id": "08ea848f",
            "name": "coin-chart-plotter",
            "path": "tool_responses/coin-technical-analyzer/08ea848f.json",
            "url": "https://data.fridon.ai/tool_responses/coin-chart-plotter/4f916770.json"
        },
        "btc": {
            "type": "coin-chart-plotter",
            "source": "s3",
            "extension": "json",
            "id": "1413b313",
            "name": "coin-chart-plotter",
            "path": "tool_responses/coin-chart-plotter/1413b313.json",
            "url": "https://data.fridon.ai/tool_responses/coin-chart-plotter/1413b313.json"
        }
    }
    async def arun(self, coin_name: str,*args, **kwargs) -> dict:
        if coin_name not in self.coin_analysis:
            return "We don't support this coin yet."
        return self.coin_analysis[coin_name]
