from typing import Union

from libs.community.helpers.utilities import DatetimeExtractorUtility
from libs.core.plugins.schemas import BaseToolInput
from libs.core.plugins.tools import BaseTool
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
    coin_name: str
    start_date: Union[str, None] = None


CoinPriceChartSimilaritySearchTool = BaseTool(
    name="coin-price-chart-similarity-search",
    description="A tool that allows you to search for similar coins by price chart of the given time range",
    args_schema=CoinPriceChartSimilaritySearchToolInput,
    utility=CoinPriceChartSimilaritySearchUtility(),
    examples=[
        {
            "request": "Give me coins similar to bonk price chart from december 2023",
            "response": "",
        },
        {
            "request": "Show me coins similar to solana price chart",
            "response": "",
        }
    ]
)


class DatetimeExtractorToolInput(BaseToolInput):
    user_input: str

DatetimeExtractorTool = BaseTool(
    name="datetime-extractor",
    description="Use only when user mentions date and extraction is needed",
    args_schema=DatetimeExtractorToolInput,
    utility=DatetimeExtractorUtility()
)


TOOLS = [CoinPriceChartSimilaritySearchTool, DatetimeExtractorTool]