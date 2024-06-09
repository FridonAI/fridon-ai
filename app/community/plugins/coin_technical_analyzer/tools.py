from app.community.plugins.coin_technical_analyzer.utilities import CoinTechnicalAnalyzerUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class CoinTechnicalAnalyzerToolInput(BaseToolInput):
    coin_name: str


CoinTechnicalAnalyzerTool = BaseTool(
    name="CoinTechnicalAnalyzer",
    description="A utility that allows you to analyze coin by technical indicators",
    args_schema=CoinTechnicalAnalyzerToolInput,
    utility=CoinTechnicalAnalyzerUtility(),
    examples=["analyze sol price chat for me", "what do you think about sol price?"]
)

TOOLS = [CoinTechnicalAnalyzerTool]

