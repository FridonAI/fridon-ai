from datetime import datetime, timedelta
from typing import Literal

import pandas as pd
import pandas_ta as ta
import requests

from app.community.plugins.coin_technical_analyzer.data import ensure_data_store
from app.community.plugins.coin_technical_analyzer.helpers.llm import get_filter_chain
from app.core.plugins.utilities.base import BaseUtility
from app.core.plugins.utilities.llm import LLMUtility


class CoinTechnicalAnalyzerUtility(LLMUtility):
    llm_job_description = """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
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

    def _read_ohlcv_date(self, symbol: str) -> pd.DataFrame:
        time_to = int(datetime.now().timestamp())
        time_from = int((time_to - timedelta(days=120).total_seconds()))
        resp = requests.get(
            f"https://api.kraken.com/0/public/OHLC?pair={symbol.upper()}USD&interval=1440&since={time_from}"
        )

        response_data = resp.json()

        if resp.status_code != 200 or len(response_data['error']) > 0:
            raise Exception(f"Failed to fetch data from Kraken API. Status code: {resp.status_code}")

        data = list(response_data["result"].values())[0]
        df = pd.DataFrame(
            data,
            columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"],
        )
        df.drop(columns=["vwap", "count"], inplace=True)
        df.rename(columns={"time": "date"}, inplace=True)
        df["date"] = pd.to_datetime(df["date"], unit="s")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        df.set_index("date", inplace=True)
        df = df.iloc[:-1]
        return df

    async def _arun(self, coin_name: str, *args, **kwargs) -> dict:
        df = self._read_ohlcv_date(coin_name)
        df.ta.macd(append=True)
        df.ta.rsi(append=True)
        df.ta.bbands(append=True)
        df.ta.obv(append=True)

        df.ta.sma(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.stoch(append=True)
        df.ta.adx(append=True)

        df.ta.willr(append=True)
        df.ta.cmf(append=True)
        df.ta.psar(append=True)

        df["OBV_in_million"] = df["OBV"] / 1e7
        df["MACD_histogram_12_26_9"] = df["MACDh_12_26_9"]

        last_day_summary = df.iloc[-1][
            [
                "close",
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
        ]

        return {"last_day_summary": str(last_day_summary), "symbol": coin_name}


class CoinTechnicalIndicatorsListUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> list:
        return [
            "close",
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


class CoinTechnicalIndicatorsSearchUtility(BaseUtility):
    async def arun(self, filter: str, *args, **kwargs) -> list[dict]:
        token_summaries = ensure_data_store().read_token_summaries()

        chain = get_filter_chain()

        results = []

        for i in range(0, len(token_summaries), 5):
            batch = token_summaries[i : i + 5]

            curr_results = await chain.abatch([{**x, "filter": filter} for x in batch])

            results.extend([x.dict() for x in curr_results if x.binary_score == 'yes'])

        return results


class CoinBulishSearchUtility(BaseUtility):
    async def arun(self, filter: Literal["strong bulish", "bullish", "neutral", "bearish", "strong bearish"], *args, **kwargs) -> list[dict]:
        token_tags = ensure_data_store().read_token_tags()

        return [x for x in token_tags if x["tag"] == filter]
