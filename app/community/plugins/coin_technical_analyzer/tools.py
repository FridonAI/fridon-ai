from typing import Literal

from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool
from app.settings import settings

from app.community.plugins.coin_technical_analyzer.utilities import (
    CoinTechnicalIndicatorsListUtility,
    CoinTechnicalIndicatorsSearchUtility,
    CoinBulishSearchUtility
)

if settings.ENV == 'mock':
    from app.community.plugins.coin_technical_analyzer.mock.utilities import CoinTechnicalAnalyzerMockUtility as CoinTechnicalAnalyzerUtility
else:
    from app.community.plugins.coin_technical_analyzer.utilities import CoinTechnicalAnalyzerUtility

class CoinTechnicalAnalyzerToolInput(BaseToolInput):
    coin_name: str


CoinTechnicalAnalyzerTool = BaseTool(
    name="coin-technical-analyzer",
    description="A utility that allows you to analyze coin by technical indicators",
    args_schema=CoinTechnicalAnalyzerToolInput,
    utility=CoinTechnicalAnalyzerUtility(),
    examples=[
        {
            "request": "what about bonk coin?",
            "response": "",
            "image_url": "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/example-images/chart-analyzer.png",
        },
        {
            "request": "analyze bonk price chat for me",
            "response": "",
        },
        {
            "request": "what do you think about sol price?",
            "response": "",
        },
    ]
)


class CoinTechnicalIndicatorsListToolInput(BaseToolInput):
    pass


CoinTechnicalIndicatorsListTool = BaseTool(
    name="coin-technical-indicators-list",
    description="A utility that allows you to list all available coin technical indicators",
    args_schema=CoinTechnicalIndicatorsListToolInput,
    utility=CoinTechnicalIndicatorsListUtility(),
    examples=[
        {
            "request": "list technical indicators",
            "response": "",
        },
        {
            "request": "what are the technical indicators?",
            "response": "",
        },
    ]
)


class CoinTechnicalIndicatorsSearchToolInput(BaseToolInput):
    filter: str


CoinTechnicalIndicatorsSearchTool = BaseTool(
    name="coin-technical-indicators-search",
    description="A utility that allows you to search coins by technical indicators",
    args_schema=CoinTechnicalIndicatorsSearchToolInput,
    utility=CoinTechnicalIndicatorsSearchUtility(),
    examples=[
        {
            "request": "What are coins that have RSI > 30?",
            "response": "",
            "image_url": "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/example-images/search-coins-by-indicators.png",
        },
        {
            "request": "List all coins havind MACD > 0 and RSI < 10",
            "response": "",
        },
    ]
)

class CoinBullishSearchToolInput(BaseToolInput):
    filter: Literal["strong bullish", "bullish", "neutral", "bearish", "strong bearish"]


CoinBullishSearchTool = BaseTool(
    name="coin-bullish-search",
    description="A utility that allows you to search coins by technical indicators",
    args_schema=CoinBullishSearchToolInput,
    utility=CoinBulishSearchUtility(),
    examples=[
        {
            "request": "Show me bulish coins",
            "response": "",
            "image_url": "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/example-images/bullish-coins.png",
        },
        {
            "request": "What are bullish coins for this moment?",
            "response": "",

        },
        {
            "request": "Give me strongly bearish coins",
            "response": ""
        }
    ]
)


TOOLS = [
    CoinTechnicalAnalyzerTool,
    CoinTechnicalIndicatorsListTool,
    CoinTechnicalIndicatorsSearchTool,
    CoinBullishSearchTool,
]
