from typing import List, Literal

from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from fridonai_core.plugins.tools.response_dumper_base import S3ResponseDumper
from pydantic import Field

from settings import settings

if settings.ENV == "mock":
    from libs.community.plugins.coin_technical_analyzer.mock.utilities import (
        CoinTechnicalIndicatorsListMockUtility as CoinTechnicalIndicatorsListUtility,
        CoinTechnicalAnalyzerMockUtility as CoinTechnicalAnalyzerUtility,
        CoinTechnicalIndicatorsSearchMockUtility as CoinTechnicalIndicatorsSearchUtility,
        CoinChartPlotterMockUtility as CoinChartPlotterUtility,
    )
    
else:
    from libs.community.plugins.coin_technical_analyzer.utilities import (
        CoinTechnicalAnalyzerUtility,
        CoinTechnicalIndicatorsListUtility,
        CoinTechnicalIndicatorsSearchUtility,
        CoinChartPlotterUtility,
    )


class CoinTechnicalAnalyzerToolInput(BaseToolInput):
    coin_name: str = Field(..., description="The name of the coin to analyze")
    interval: Literal["1h", "4h", "1d", "1w"] = Field(
        default="1h", description="The interval of the technical indicators"
    )


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
    ],
    response_dumper=S3ResponseDumper(),
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
    ],
)


class CoinChartPlotterToolInput(BaseToolInput):
    coin_name: str = Field(..., description="The name of the coin to plot")
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
    ],
    response_dumper=S3ResponseDumper(),
)


TOOLS = [
    CoinTechnicalAnalyzerTool,
    CoinTechnicalIndicatorsListTool,
    CoinTechnicalIndicatorsSearchTool,
    CoinChartPlotterTool,
]
