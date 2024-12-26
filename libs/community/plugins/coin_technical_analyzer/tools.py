from typing import List, Literal, Union

from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from fridonai_core.plugins.tools.response_dumper_base import S3ResponseDumper
from pydantic import Field

from libs.community.plugins.coin_technical_analyzer.utilities import CoinInfoUtility
from libs.community.helpers.tools import DatetimeExtractorTool
from settings import settings

if settings.ENV == "mock":
    from libs.community.plugins.coin_technical_analyzer.mock.utilities import (
        CoinTechnicalIndicatorsListMockUtility as CoinTechnicalIndicatorsListUtility,
        CoinTechnicalAnalyzerMockUtility as CoinTechnicalAnalyzerUtility,
        CoinChartPlotterMockUtility as CoinChartPlotterUtility,
    )
    
else:
    from libs.community.plugins.coin_technical_analyzer.utilities import (
        CoinTechnicalAnalyzerUtility,
        CoinTechnicalIndicatorsListUtility,
        CoinChartPlotterUtility,
    )


class CoinTechnicalAnalyzerToolInput(BaseToolInput):
    coin_name: str = Field(..., description="The symbol of the coin to analyze, abbreviation. If full name is provided refactor to abbreviation.")
    interval: Literal["1h", "4h", "1d", "1w"] = Field(
        default="1h", description="The timeframe of the chart candles"
    )
    start_time: Union[str, None] = Field(
        default=None, description="The start time of the price chart"
    )
    end_time: Union[str, None] = Field(
        default=None, description="The end time of the price chart"
    )


CoinTechnicalAnalyzerTool = BaseTool(
    name="coin-technical-analyzer",
    description="A utility that allows you to analyze coin by technical indicators",
    args_schema=CoinTechnicalAnalyzerToolInput,
    utility=CoinTechnicalAnalyzerUtility(),
    examples=[
        {
            "request": "What about bonk coin price chart?",
            "response": "",
            "image_url": "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/example-images/chart-analyzer.png",
        },
        {
            "request": "Analyze bonk price chat for me from 2024-01-01 to 2024-01-02",
            "response": "",
        },
        {
            "request": "What do you think about sol price?",
            "response": "",
        },
        {
            "request": "Analyze solana price chart from 12 December 2024 to 13 December 2024 by 4h timeframe",
            "response": "",
        },
    ],
    response_dumper=S3ResponseDumper(),
)


class CoinTechnicalIndicatorsListToolInput(BaseToolInput):
    indicator_name: Union[Literal[
        "MACD_12_26_9",
        "MACD_histogram_12_26_9",
        "RSI_14",
        "BBL_5_2.0",
        "BBM_5_2.0",
        "BBU_5_2.0",
        "SMA_20",
        "EMA_50",
        "OBV_in_million",
        "STOCHk_14_3_3",
        "STOCHd_14_3_3",
        "ADX_14",
        "WILLR_14",
        "CMF_20",
        "PSARl_0.02_0.2",
        "PSARs_0.02_0.2",
    ], None] = Field(default=None, description="The name of the technical indicator to get description of")


CoinTechnicalIndicatorsListTool = BaseTool(
    name="coin-technical-indicators-list",
    description="A utility that provides information about coin technical indicators, including a comprehensive list, detailed descriptions of specific or all indicators.",
    args_schema=CoinTechnicalIndicatorsListToolInput,
    utility=CoinTechnicalIndicatorsListUtility(),
    examples=[
        {
            "request": "List technical indicators",
            "response": "",
        },
        {
            "request": "What are the technical indicators?",
            "response": "",
        },
        {
            "request": "What is MACD_12_26_9?",
            "response": "",
        },
        {
            "request": "When is RSI_14 used?",
            "response": "",
        },
    ],
)


class CoinChartPlotterToolInput(BaseToolInput):
    coin_name: str = Field(..., description="The symbol of the coin to plot, abbreviation. If full name is provided refactor to abbreviation.")
    indicators: List[
        Literal[
            "MACD_12_26_9",
            "MACD_histogram_12_26_9",
            "RSI_14",
            "BBL_5_2.0",
            "BBM_5_2.0",
            "BBU_5_2.0",
            "SMA_20",
            "EMA_50",
            "OBV_in_million",
            "STOCHk_14_3_3",
            "STOCHd_14_3_3",
            "ADX_14",
            "WILLR_14",
            "CMF_20",
            "PSARl_0.02_0.2",
            "PSARs_0.02_0.2",
        ]
    ] = Field(
        default=[
            "MACD_12_26_9",
            "MACD_histogram_12_26_9",
            "RSI_14",
            "BBL_5_2.0",
            "BBM_5_2.0",
            "BBU_5_2.0",
            "SMA_20",
            "EMA_50",
            "OBV_in_million",
            "STOCHk_14_3_3",
            "STOCHd_14_3_3",
            "ADX_14",
            "WILLR_14",
            "CMF_20",
            "PSARl_0.02_0.2",
            "PSARs_0.02_0.2",
        ],
        description="List of indicator names to be visualized on the chart.",
    )
    interval: Literal["1h", "4h", "1d", "1w"] = Field(
        default="4h", description="The interval of the technical indicators"
    )



CoinChartPlotterTool = BaseTool(
    name="coin-chart-plotter",
    description="A utility that allows you to plot coin chart",
    args_schema=CoinChartPlotterToolInput,
    utility=CoinChartPlotterUtility(),
    examples=[
        {
            "request": "Plot BTC chart",
            "response": "",
        },
        {
            "request": "Give me graph for solana with RSI, MACD and SMA indicators",
            "response": "",
        },
        {
            "request": "Plot BTC chart.",
        }
    ],
    response_dumper=S3ResponseDumper(),
)

class CoinInfoToolInput(BaseToolInput):
    coin_name: str = Field(
        ...,
        description="The symbol of the coin to get info about, abbreviation. If full name is provided refactor to abbreviation.",
    )
    fields: List[
        Literal[
            "price",
            "description",
            "volume",
            "MACD_12_26_9",
            "MACD_histogram_12_26_9",
            "RSI_14",
            "BBL_5_2.0",
            "BBM_5_2.0",
            "BBU_5_2.0",
            "SMA_20",
            "EMA_50",
            "OBV_in_million",
            "STOCHk_14_3_3",
            "STOCHd_14_3_3",
            "ADX_14",
            "WILLR_14",
            "CMF_20",
            "PSARl_0.02_0.2",
            "PSARs_0.02_0.2",
        ]
    ] = Field(default=[], description="List of fields to get info about")


CoinInfoTool = BaseTool(
    name="coin-info",
    description="A utility that allows you to get info about coin, its description,current price, indicator values.",
    args_schema=CoinInfoToolInput,
    utility=CoinInfoUtility(),
    examples=[
        {
            "request": "What is the price of BTC?",
            "response": "",
        },
        {
            "request": "What is the price, volume and rsi value of BTC?",
            "response": "",
        },
    ],
)


TOOLS = [
    CoinTechnicalAnalyzerTool,
    CoinTechnicalIndicatorsListTool,
    CoinChartPlotterTool,
    CoinInfoTool,
    DatetimeExtractorTool,
]
