from fridonai_core.plugins.tools.response_dumper_base import S3ResponseDumper
from pydantic import Field
from typing import Literal, Union

from libs.community.helpers.tools import DatetimeExtractorTool
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from libs.community.plugins.coin_technical_chart_searcher.utilities import (
    CoinPriceChartFalshbackSearchUtility,
)
from settings import settings

if settings.ENV == 'mock':
    from libs.community.plugins.coin_technical_chart_searcher.mock.utilities import (
        CoinPriceChartSimilaritySearchMockUtility as CoinPriceChartSimilaritySearchUtility,
        CoinTechnicalIndicatorsSearchMockUtility as CoinTechnicalIndicatorsSearchUtility,
    )
else:
    from libs.community.plugins.coin_technical_chart_searcher.utilities import (
        CoinPriceChartSimilaritySearchUtility,
        CoinTechnicalIndicatorsSearchUtility,
    )

class CoinPriceChartSimilaritySearchToolInput(BaseToolInput):
    coin_name: str = Field(description="The symbol of the coin, abbreviation. If full name is provided refactor to abbreviation.")
    interval: Literal["1h", "4h", "1d", "1w"] = Field(
        default="1d", description="The interval of the price chart"
    )
    start_time: Union[str, None] = Field(
        default=None, description="The start date for the price chart comparison."
    )
    end_time: Union[str, None] = Field(
        default=None, description="The end date for the price chart comparison."
    )

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
            "request": "Give me coins similar to solana 4h price chart from 2024-11-12 12:04:00",
            "response": "",
        },
        {
            "request": "Which coins look like wif price chart ending on 2024 december 12?",
            "response": "",
        },
    ],
)

class CoinPriceChartFlashbackSearchToolInput(BaseToolInput):
    coin_name: str = Field(
        description="The symbol of the coin, abbreviation. If full name is provided refactor to abbreviation."
    )
    interval: Literal["1h", "4h", "1d", "1w"] = Field(
        default="1d", description="The interval of the price chart"
    )
    chart_length: int = Field(default=30, description="The length of the price chart")


CoinPriceChartFlashbackSearchTool = BaseTool(
    name="coin-price-chart-flashback-search",
    description="A tool that identifies historical moments when other cryptocurrencies displayed price patterns similar to a given coin's current chart structure, helping spot potential market behavior patterns.",
    args_schema=CoinPriceChartFlashbackSearchToolInput,
    utility=CoinPriceChartFalshbackSearchUtility(),
    response_dumper=S3ResponseDumper(),
    examples=[
        {
            "request": "Show me historical crypto patterns similar to SOL's current daily chart",
            "response": "",
        },
        {
            "request": "Which coins in the past had similar 4-hour chart patterns to what BTC is showing in the last 30 days?",
            "response": "",
        },
    ],
)


class CoinTechnicalIndicatorsSearchToolInput(BaseToolInput):
    interval: Literal["1h", "4h", "1d", "1w"] = Field(
        default="1h", description="The interval of the technical indicators"
    )
    filter: str = Field(
        ..., description="The filter text query to use for the technical indicators"
    )


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
        {
            "request": "Search coins with RSI < 30",
            "response": "",
        },
        {
            "request": "Give me coins with EMA > 100",
            "response": "",
        }
    ],
)


TOOLS = [
    CoinPriceChartSimilaritySearchTool,
    CoinTechnicalIndicatorsSearchTool,
    CoinPriceChartFlashbackSearchTool,
    DatetimeExtractorTool,
]
