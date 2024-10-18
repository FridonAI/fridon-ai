from fridonai_core.plugins.tools.response_dumper_base import S3ResponseDumper
from pydantic import Field
from typing import Union

from libs.community.helpers.utilities import DatetimeExtractorUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from settings import settings

if settings.ENV == 'mock':
    from libs.community.plugins.coin_price_chart_similarity_search.mock.utilities import (
        CoinPriceChartSimilaritySearchMockUtility as CoinPriceChartSimilaritySearchUtility,
    )
else:
    from libs.community.plugins.coin_price_chart_similarity_search.utilities import (
        CoinPriceChartSimilaritySearchUtility,
    )

class CoinPriceChartSimilaritySearchToolInput(BaseToolInput):
    coin_name: str = Field(description="The symbol of the coin, abbreviation. If full name is provided refactor to abbreviation.")
    start_date: Union[str, None] = Field(default=None, description="The start date for the price chart comparison.")


CoinPriceChartSimilaritySearchTool = BaseTool(
    name="coin-price-chart-similarity-search",
    description="A tool that finds coins with current price charts similar to a given coin’s current or past price chart.",
    args_schema=CoinPriceChartSimilaritySearchToolInput,
    utility=CoinPriceChartSimilaritySearchUtility(),
    response_dumper=S3ResponseDumper(),
    examples=[
        {
            "request": "Give me coins similar to bonk price chart from december 2023",
            "response": "",
        },
        {
            "request": "Give me coins similar to solana price chart",
            "response": "",
        },
        {
            "request": "Which coins look like wif price chart two months ago?",
            "response": "",
        },
    ]
)


class DatetimeExtractorToolInput(BaseToolInput):
    user_input: str

DatetimeExtractorTool = BaseTool(
    name="datetime-extractor",
    description="Helper tool to extract date from user input. Use only when user mentions date and extraction is needed",
    args_schema=DatetimeExtractorToolInput,
    utility=DatetimeExtractorUtility()
)


TOOLS = [CoinPriceChartSimilaritySearchTool, DatetimeExtractorTool]
