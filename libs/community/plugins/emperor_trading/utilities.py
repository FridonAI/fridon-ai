import pandas as pd
from datetime import datetime, timedelta, UTC
from fridonai_core.plugins.utilities import LLMUtility
from libs.data_providers.coin_price_providers import BinanceCoinPriceDataProvider

from libs.internals.indicators.emperor_guide import (
    get_latest_ema_crossover,
    check_200ema_support,
)

from libs.community.plugins.emperor_trading.prompts import emas_guide_prompt


class EmperorTradingCoinAnalysisUtility(LLMUtility):
    llm_job_description: str = emas_guide_prompt
    model_name: str = "gpt-4o"
    result_as_test_str: bool = True

    async def _arun(
        self, coin_name: str, end_time: str | None = None, *args, **kwargs
    ) -> str:
        current_time = datetime.now(UTC)
        if end_time is not None:
            end_time = datetime.fromisoformat(end_time).replace(tzinfo=UTC)
        else:
            end_time = current_time

        (
            coin_historical_ohlcvs_4h,
            coin_historical_ohlcvs_1d,
        ) = await self.get_coin_historical_ohlcvs(coin_name, end_time)

        chart_results = await self.calculate_indicators(
            coin_historical_ohlcvs_4h, coin_historical_ohlcvs_1d, end_time
        )

        print("chart_results", chart_results)

        return {"chart_results": chart_results, "coin_name": coin_name}

    async def calculate_indicators(
        self,
        coin_historical_ohlcvs_4h: pd.DataFrame,
        coin_historical_ohlcvs_1d: pd.DataFrame,
        end_time: datetime,
    ) -> str:
        ema_results = self.get_ema_results(
            coin_historical_ohlcvs_4h, coin_historical_ohlcvs_1d, end_time
        )
        return {**ema_results}

    async def get_coin_historical_ohlcvs(
        self, coin_name: str, end_time: datetime
    ) -> pd.DataFrame:
        binance_provider = BinanceCoinPriceDataProvider()
        coin_historical_ohlcvs_4h = (
            await binance_provider.get_historical_ohlcv_by_start_end(
                [coin_name],
                interval="4h",
                start_time=end_time - timedelta(days=60),
                end_time=end_time,
                output_format="dataframe",
            )
        )
        coin_historical_ohlcvs_1d = (
            await binance_provider.get_historical_ohlcv_by_start_end(
                [coin_name],
                interval="1d",
                start_time=end_time - timedelta(days=200),
                end_time=end_time,
                output_format="dataframe",
            )
        )

        coin_historical_ohlcvs_4h.columns = [
            col.capitalize() for col in coin_historical_ohlcvs_4h.columns
        ]
        coin_historical_ohlcvs_1d.columns = [
            col.capitalize() for col in coin_historical_ohlcvs_1d.columns
        ]

        return coin_historical_ohlcvs_4h, coin_historical_ohlcvs_1d

    def get_ema_results(
        self,
        coin_historical_ohlcvs_4h: pd.DataFrame,
        coin_historical_ohlcvs_1d: pd.DataFrame,
        end_time: datetime,
    ) -> str:
        ema_crossover_result = get_latest_ema_crossover(
            coin_historical_ohlcvs_1d,
            int((end_time - timedelta(days=100)).timestamp() * 1000),
        )
        ema_support_result = check_200ema_support(coin_historical_ohlcvs_4h)
        return {
            "ema_13_21_crossover_result_ohlcv_1d": ema_crossover_result,
            "ema_200_support_result_ohlcv_4h": ema_support_result,
        }
