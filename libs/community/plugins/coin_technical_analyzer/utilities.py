from datetime import datetime, timedelta
from typing import Literal

import pandas as pd
import pandas_ta as ta
import polars as pl
import pyarrow.compute as pc
import requests
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

Given {symbol} TA data as below on the last trading day, what will be the next few days possible crypto price movement?

Summary of Technical Indicators for the Last Day:
{last_day_summary}"""

    async def _arun(
        self, coin_name: str, interval: Literal["1h", "4h", "1d", "1w"], *args, **kwargs
    ) -> dict:
        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )

        delta = {
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "1d": timedelta(days=1),
            "1w": timedelta(days=7),
        }[interval]

        # df = indicators_repository.read(filters=(pc.field("coin") == coin_name) & (pc.field("timestamp") > int((datetime.now() - delta).timestamp() * 1000)))
        df = indicators_repository.read(
            filters=(pc.field("coin") == coin_name)
            & (
                pc.field("timestamp")
                >= int((datetime.utcnow() - delta).timestamp() * 1000)
            )
            & (pc.field("timestamp") <= int(datetime.utcnow().timestamp() * 1000))
        )

        if len(df) == 0:
            return "No data found"

        print(str(df.to_dicts()))

        return {"last_day_summary": str(df.to_dicts()), "symbol": coin_name}


class CoinTechnicalIndicatorsListUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> list:
        return [
            field
            for field in IndicatorsRepository.table_schema
            if field not in ["coin", "date", "timestamp", "reason"]
        ]


class CoinTechnicalIndicatorsSearchUtility(BaseUtility):
    async def arun(
        self, interval: Literal["1h", "4h", "1d", "1w"], filter: str, *args, **kwargs
    ) -> list[dict]:
        filter_generation_chain = get_filter_generator_chain()

        repository = IndicatorsRepository(table_name=f"indicators_{interval}")

        filter_expression = filter_generation_chain.invoke(
            {"schema": repository.table_schema, "query": filter}
        ).filters

        print(filter_expression)

        delta = {
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "1d": timedelta(days=1),
            "1w": timedelta(days=7),
        }[interval]

        results = repository.read(
            filters=eval(filter_expression)
            & (
                pc.field("timestamp")
                >= int((datetime.utcnow() - delta).timestamp() * 1000)
            )
            & (pc.field("timestamp") <= int(datetime.utcnow().timestamp() * 1000))
        )

        latest_records = results.sort("timestamp").group_by("coin").agg(pl.all().last())

        if len(latest_records) == 0:
            return "No coins found"

        return latest_records.to_dicts()


class CoinBulishSearchUtility(BaseUtility):
    async def arun(
        self,
        filter: Literal[
            "strong bulish", "bullish", "neutral", "bearish", "strong bearish"
        ],
        *args,
        **kwargs,
    ) -> list[dict]:
        token_tags = ensure_data_store().read_token_tags()

        return [x for x in token_tags if x["tag"] == filter]
