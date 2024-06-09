from app.community.plugins.coin_technical_analyzer.utilities import (
    CoinTechnicalAnalyzerUtility,
    CoinTechnicalIndicatorsListUtility,
    CoinTechnicalIndicatorsSearchUtility,
)
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class CoinTechnicalAnalyzerToolInput(BaseToolInput):
    coin_name: str


CoinTechnicalAnalyzerTool = BaseTool(
    name="CoinTechnicalAnalyzer",
    description="A utility that allows you to analyze coin by technical indicators",
    args_schema=CoinTechnicalAnalyzerToolInput,
    utility=CoinTechnicalAnalyzerUtility(),
)


class CoinTechnicalIndicatorsListToolInput(BaseToolInput):
    pass


CoinTechnicalIndicatorsListTool = BaseTool(
    name="CoinTechnicalIndicatorsList",
    description="A utility that allows you to list all available coin technical indicators",
    args_schema=CoinTechnicalIndicatorsListToolInput,
    utility=CoinTechnicalIndicatorsListUtility(),
)


class CoinTechnicalIndicatorsSearchToolInput(BaseToolInput):
    filter: str


CoinTechnicalIndicatorsTool = BaseTool(
    name="CoinTechnicalIndicators",
    description="A utility that allows you to search coins by technical indicators",
    args_schema=CoinTechnicalIndicatorsSearchToolInput,
    utility=CoinTechnicalIndicatorsSearchUtility(),
)


TOOLS = [CoinTechnicalAnalyzerTool, CoinTechnicalIndicatorsListTool, CoinTechnicalIndicatorsTool]
