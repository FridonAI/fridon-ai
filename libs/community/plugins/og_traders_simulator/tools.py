from pydantic import Field
from typing import Union, List, Literal

from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from fridonai_core.plugins.tools.response_dumper_base import S3ResponseDumper

from libs.community.helpers.tools import DatetimeExtractorTool

from libs.community.plugins.og_traders_simulator.utilities import (
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
    category: List[Literal["spot", "futures"]] = Field(
        default=["spot", "futures"],
        description="The order of categories of the coin data, spot or futures data. Order is a priority of data categories.",
    )


EmperorTradingCoinAnalysisTool = BaseTool(
    name="emperor-trader-coin-analysis",
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
#     name="emperor-trader-coin-analysis-manual",
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
