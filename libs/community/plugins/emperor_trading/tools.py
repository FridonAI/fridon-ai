from pydantic import Field
from typing import Union

from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from fridonai_core.plugins.tools.response_dumper_base import S3ResponseDumper

from libs.community.helpers.tools import DatetimeExtractorTool

from libs.community.plugins.emperor_trading.utilities import (
    EmperorTradingCoinAnalysisUtility,
    # EmperorTradingManualUtility,
)


class EmperorTradingCoinAnalysisToolInput(BaseToolInput):
    coin_name: str = Field(
        description="The symbol of the coin, abbreviation. If full name is provided refactor to abbreviation."
    )
    end_time: Union[str, None] = Field(
        default=None, description="The end date for the price chart comparison."
    )


EmperorTradingCoinAnalysisTool = BaseTool(
    name="emperor-trading-coin-analysis",
    description="A tool that analyzes a coin's price chart with technical indicators, trends, and setups based on the EmperorBTC guide.",
    args_schema=EmperorTradingCoinAnalysisToolInput,
    utility=EmperorTradingCoinAnalysisUtility(),
    response_dumper=S3ResponseDumper(),
    examples=[
        {
            "request": "Analyze SOL considering the EmperorBTC guide.",
            "response": "",
        },
        {
            "request": "What can you tell me about SOL considering the EmperorBTC plugin?",
            "response": "",
        },
        {
            "request": "Analyze BTC before 10 april 2019 considering the EmperorBTC guide",
            "response": "",
        },
    ],
)


class EmperorTradingManualToolInput(BaseToolInput):
    question: str = Field(
        description="The question about EmperorBTC guide which EmperorTradingCoinAnalysis Tool uses."
    )


# EmperorTradingCoinAnalysisManualTool = BaseTool(
#     name="emperor-trading-coin-analysis-manual",
#     description="Informative tool that answers questions about the EmperorBTC guide we use for analysis.",
#     args_schema=EmperorTradingManualToolInput,
#     utility=EmperorTradingManualUtility(),
#     examples=[
#         {
#             "request": "What indicators, setups and trends are used from EmperorBTC guide?",
#             "response": "",
#         },
#         {
#             "request": "What can you tell me about EMA supports and indicators from EmperorBTC guide?",
#             "response": "",
#         },
#     ],
# )


class DatetimeExtractorToolInput(BaseToolInput):
    user_input: str


TOOLS = [
    EmperorTradingCoinAnalysisTool,
    # EmperorTradingCoinAnalysisManualTool,
    DatetimeExtractorTool,
]
