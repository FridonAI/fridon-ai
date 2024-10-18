from datetime import datetime, timedelta
from typing import List, Literal
import pyarrow.compute as pc

from fridonai_core.plugins.utilities.base import BaseUtility
from fridonai_core.plugins.utilities.llm import LLMUtility

from libs.community.plugins.coin_technical_analyzer.data import ensure_data_store
from libs.community.plugins.coin_technical_analyzer.helpers.llm import (
    get_filter_generator_chain,
)
from libs.repositories import IndicatorsRepository


class CoinTechnicalAnalyzerUtility(LLMUtility):
    llm_job_description: str = """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
Your mastery encompasses both stock fundamentals and intricate technical indicators. \
You possess the ability to decode complex market dynamics, \
providing clear insights and recommendations backed by a thorough understanding of interrelated factors. \
Your expertise extends to practical tools like the pandas_ta module, \
allowing you to navigate data intricacies with ease. \
As a TA authority, your role is to decipher market trends, make informed predictions, and offer valuable perspectives.

Generated response should be simple, easy to understand, user shouldn't try hard to understand what's happening, conclusion should be main part of the analysis.

Given {symbol} coin's TA data as below on the last trading day, what will be the next few days possible crypto price movement?

Technical Indicators for {interval} intervals:
{coin_history_indicators}"""
    fields_to_retain: list[str] = ["plot_data"]

    async def _arun(
        self,
        coin_name: str,
        interval: Literal["1h", "4h", "1d", "1w"] = "4h",
        *args,
        **kwargs,
    ) -> dict:
        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )

        coin_latest_record_df = indicators_repository.get_coin_latest_record(
            coin_name.upper()
        )

        if len(coin_latest_record_df) == 0:
            return "No data found"

        return {
            "coin_history_indicators": str(coin_latest_record_df.to_dicts()),
            "symbol": coin_name,
            "plot_data": indicators_repository.get_coin_last_records(
                coin_name.upper(), number_of_points=200
            ).to_dicts(),
            "interval": interval,
        }


class CoinTechnicalIndicatorsListUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> str:
        return "Here is the list of available technical indicators " + ', '.join([
            'MACD_12_26_9',
            'MACD_histogram_12_26_9',
            'RSI_14',
            'BBL_5_2.0',
            'BBM_5_2.0',
            'BBU_5_2.0',
            'SMA_20',
            'EMA_50',
            'OBV_in_million',
            'STOCHk_14_3_3',
            'STOCHd_14_3_3',
            'ADX_14',
            'WILLR_14',
            'CMF_20',
            'PSARl_0.02_0.2',
            'PSARs_0.02_0.2'
        ])


class CoinChartPlotterUtility(BaseUtility):
    async def arun(
        self,
        coin_name: str,
        indicators: List[str] = [],
        interval: Literal["1h", "4h", "1d", "1w"] = "4h",
        *args,
        **kwargs,
    ) -> str:
        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )
        print("Want these indicators", indicators)
        coin_last_records = indicators_repository.get_coin_last_records(
            coin_name, number_of_points=200
        )

        if len(coin_last_records) == 0:
            return "No coins found"

        return {
            "plot_data": coin_last_records.to_dicts(),
            "indicators_to_plot": indicators,
        }
