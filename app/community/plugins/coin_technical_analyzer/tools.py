from typing import Literal
from app.community.plugins.coin_technical_analyzer.utilities import (
    CoinTechnicalAnalyzerUtility,
    CoinTechnicalIndicatorsListUtility,
    CoinTechnicalIndicatorsSearchUtility,
    CoinBulishSearchUtility
)
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class CoinTechnicalAnalyzerToolInput(BaseToolInput):
    coin_name: str


CoinTechnicalAnalyzerTool = BaseTool(
    name="coin-technical-analyzer",
    description="A utility that allows you to analyze coin by technical indicators",
    args_schema=CoinTechnicalAnalyzerToolInput,
    utility=CoinTechnicalAnalyzerUtility(),
    examples=["analyze sol price chat for me", "what do you think about sol price?"]
)


class CoinTechnicalIndicatorsListToolInput(BaseToolInput):
    pass


CoinTechnicalIndicatorsListTool = BaseTool(
    name="coin-technical-indicators-list",
    description="A utility that allows you to list all available coin technical indicators",
    args_schema=CoinTechnicalIndicatorsListToolInput,
    utility=CoinTechnicalIndicatorsListUtility(),
    examples=["list all technical indicators", "what are the technical indicators?"]
)


class CoinTechnicalIndicatorsSearchToolInput(BaseToolInput):
    filter: str


CoinTechnicalIndicatorsSearchTool = BaseTool(
    name="coin-technical-indicators-search",
    description="A utility that allows you to search coins by technical indicators",
    args_schema=CoinTechnicalIndicatorsSearchToolInput,
    utility=CoinTechnicalIndicatorsSearchUtility(),
    examples=["What are coins that have RSI > 30?", "List all coins havind MACD > 0 and RSI < 10"]
)

class CoinBullishSearchToolInput(BaseToolInput):
    filter: Literal["strong bullish", "bullish", "neutral", "bearish", "strong bearish"]


CoinBullishSearchTool = BaseTool(
    name="coin-bullish-search",
    description="A utility that allows you to search coins by technical indicators",
    args_schema=CoinBullishSearchToolInput,
    utility=CoinBulishSearchUtility(),
    examples=["Show me bulish coins", "What are bulish coins for this moment?", "Give me strongly bearish coins"]
)


TOOLS = [
    CoinTechnicalAnalyzerTool,
    CoinTechnicalIndicatorsListTool,
    CoinTechnicalIndicatorsSearchTool,
    CoinBullishSearchTool,
]
