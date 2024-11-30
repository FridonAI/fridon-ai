import pyarrow.compute as pc
from datetime import UTC, datetime, timedelta
from typing import List, Literal, Tuple, Union

import stumpy
import numpy as np
import pandas as pd


from fridonai_core.plugins.utilities import BaseUtility
from libs.community.plugins.coin_technical_analyzer.helpers.llm import get_filter_generator_chain
from libs.data_providers.coin_price_providers import BinanceCoinPriceDataProvider
from libs.repositories.indicators import IndicatorsRepository

from libs.community.plugins.coin_technical_chart_searcher.helper import (
    similarity_search_coins,
)


def _find_similar_pattern(
    source_prices: Union[list, np.ndarray],
    target_prices: Union[list, np.ndarray],
    max_matches: int = 10,
) -> List[Tuple[int, float]]:
    source = np.array(source_prices)
    target = np.array(target_prices)

    pattern_length = len(source) - 1
    if pattern_length >= len(target):
        raise ValueError("Pattern length must be shorter than both price series")

    query = source[-pattern_length:]

    try:
        stumpy.config.STUMPY_EXCL_ZONE_DENOM = np.inf

        matches_top = stumpy.match(
            query,
            target,
            max_distance=np.inf,
            max_matches=max_matches,
        )

        stumpy.config.STUMPY_EXCL_ZONE_DENOM = 4

        return matches_top

    except Exception as e:
        print(f"Error during pattern matching: {str(e)}")
        return None, None


class CoinPriceChartSimilaritySearchUtility(BaseUtility):
    interval_to_params: dict[Literal["1h", "4h", "1d", "1w"], dict] = {
        "1h": {
            "chart_length": 2,
        },
        "4h": {
            "chart_length": 10,
        },
        "1d": {
            "chart_length": 30,
        },
        "1w": {
            "chart_length": 114,
        },
    }

    async def arun(
        self,
        coin_name: str,
        *args,
        start_time: str | None = None,
        end_time: str | None = None,
        interval: Literal["1h", "4h", "1d", "1w"] = "1d",
        **kwargs,
    ) -> str | dict:
        current_time = datetime.now(UTC)
        hours_length = self.interval_to_params[interval]["chart_length"] * 24

        if start_time is not None and end_time is not None:
            start_time = datetime.fromisoformat(start_time).replace(tzinfo=UTC)
            end_time = datetime.fromisoformat(end_time).replace(tzinfo=UTC)
            if start_time > end_time:
                start_time, end_time = end_time, start_time

        elif start_time is not None:
            start_time = datetime.fromisoformat(start_time).replace(tzinfo=UTC)
            end_time = min(start_time + timedelta(hours=hours_length), current_time)

        else:
            end_time = (
                datetime.fromisoformat(end_time)
                if end_time is not None
                else current_time
            )
            if end_time > current_time:
                end_time = current_time
            start_time = end_time - timedelta(hours=hours_length)

        time_diff_hours = (end_time - start_time).total_seconds() / 3600
        current_minus_diff_time = current_time - timedelta(hours=time_diff_hours)

        binance_provider = BinanceCoinPriceDataProvider()
        target_coins = [coin for coin in similarity_search_coins if coin != coin_name][
            :100
        ]

        source_coin_historical_ohlcvs = (
            await binance_provider.get_historical_ohlcv_by_start_end(
                [coin_name],
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                output_format="dataframe",
            )
        )

        if source_coin_historical_ohlcvs.shape[0] == 0:
            return "No data found"

        target_coins_historical_ohlcvs = (
            await binance_provider.get_historical_ohlcv_by_start_end(
                target_coins,
                interval=interval,
                start_time=current_minus_diff_time,
                end_time=current_time,
                output_format="dataframe",
            )
        )
        target_start_time = int(
            target_coins_historical_ohlcvs.iloc[0]["timestamp"] / 1000
        )
        target_end_time = int(
            target_coins_historical_ohlcvs.iloc[-1]["timestamp"] / 1000
        )
        all_matches = []

        source_shape = source_coin_historical_ohlcvs.shape

        for coin in target_coins:
            target_ohlcvs = target_coins_historical_ohlcvs[
                target_coins_historical_ohlcvs["coin"] == coin
            ]
            if target_ohlcvs.shape[0] < source_shape[0] - 2:
                print("Skipping coin: ", coin)
                continue
            if target_ohlcvs.shape[0] > source_shape[0]:
                target_ohlcvs = target_ohlcvs.tail(source_shape[0]).reset_index(
                    drop=True
                )
            elif target_ohlcvs.shape[0] < source_shape[0]:
                source_coin_historical_ohlcvs = source_coin_historical_ohlcvs.tail(
                    target_ohlcvs.shape[0]
                ).reset_index(drop=True)
            matches = _find_similar_pattern(
                source_coin_historical_ohlcvs["close"].values,
                target_ohlcvs["close"].values,
            )

            if matches is None or len(matches) == 0:
                continue

            try:
                all_matches.append(
                    {
                        "dist": matches[0][0],
                        "coin": coin,
                    }
                )
            except Exception as e:
                print("Error with coin: ", coin, "Error: ", e)
                continue

        sorted_results = sorted(all_matches, key=lambda x: x["dist"])[:3]

        return {
            "type": "similar_coins",
            "coin": coin_name,
            "interval": interval,
            "start_date_timestamp": int(start_time.timestamp()),
            "end_date_timestamp": int(end_time.timestamp()),
            "start_date": start_time.strftime("%d %B %Y"),
            "end_date": end_time.strftime("%d %B %Y"),
            "similar_coins": [
                {
                    "symbol": match["coin"],
                    "score": match["dist"],
                    "start_time": target_start_time,
                    "end_time": target_end_time,
                }
                for match in sorted_results
            ],
        }


class CoinTechnicalIndicatorsSearchUtility(BaseUtility):
    async def arun(
        self, filter: str, interval: Literal["1h", "4h", "1d", "1w"] = "4h", *args, **kwargs
    ) -> list[dict]:
        filter_generation_chain = get_filter_generator_chain()

        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )

        filter_expression = filter_generation_chain.invoke(
            {"schema": indicators_repository.table_schema, "query": filter}
        ).filters

        print("Filter expression: ", filter_expression)

        latest_records = indicators_repository.get_the_latest_records(
            eval(filter_expression),
            last_n=True,
        )

        if len(latest_records) == 0:
            return "No coins found"

        records = latest_records.to_dicts()

        result_text = f"Here are {len(records)} coins with the given filters (filter): "

        for i, record in enumerate(records):
            result_text += "******\n"

            for key, value in record.items():
                if i > 2 and key != "coin":
                    continue
                result_text += f"{key}: {value}\n"

        return result_text


class CoinPriceChartFalshbackSearchUtility(BaseUtility):
    days_to_points_for_interval: dict[Literal["1h", "4h", "1d", "1w"], int] = {
        "1h": 24,
        "4h": 6,
        "1d": 1,
        "1w": 1 / 7,
    }

    interval_to_params: dict[Literal["1h", "4h", "1d", "1w"], dict] = {
        "1h": {
            "fetch_days": 250,
            "ending_days_offset": 2,
            "chart_length": 2,
            "allowed_day_difference": 4,
        },
        "4h": {
            "fetch_days": 500,
            "ending_days_offset": 4,
            "chart_length": 10,
            "allowed_day_difference": 10,
        },
        "1d": {
            "fetch_days": 2000,
            "ending_days_offset": 100,
            "chart_length": 30,
            "allowed_day_difference": 30,
        },
        "1w": {
            "fetch_days": 4000,
            "ending_days_offset": 200,
            "chart_length": 114,
            "allowed_day_difference": 70,
        },
    }

    og_coins_for_flashback: list[str] = ["BTC", "ETH", "SOL", "DOGE"]

    async def arun(
        self,
        coin_name: str,
        *args,
        interval: Literal["1h", "4h", "1d", "1w"] = "1d",
        chart_length: int | None = None,
        **kwargs,
    ) -> list[dict]:
        if chart_length is None:
            chart_length = self.interval_to_params[interval]["chart_length"]

        number_of_points = chart_length * self.days_to_points_for_interval[interval]
        coins_to_fetch = [
            coin for coin in self.og_coins_for_flashback if coin != coin_name
        ]
        binance_provider = BinanceCoinPriceDataProvider()

        def convert_timestamp_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
            df["datetime"] = pd.to_datetime(
                df["timestamp"] / 1000, unit="s"
            ).dt.strftime("%Y-%m-%d %H:%M:%S")
            return df

        og_coins_historical_ohlcvs = await binance_provider.get_historical_ohlcv(
            coins_to_fetch,
            interval=interval,
            days=self.interval_to_params[interval]["fetch_days"],
            output_format="dataframe",
        )
        og_coins_historical_ohlcvs = convert_timestamp_to_datetime(
            og_coins_historical_ohlcvs
        )

        current_coin_historical_ohlcv = await binance_provider.get_historical_ohlcv(
            [coin_name],
            interval=interval,
            days=self.interval_to_params[interval]["fetch_days"],
            output_format="dataframe",
        )
        current_coin_historical_ohlcv = convert_timestamp_to_datetime(
            current_coin_historical_ohlcv
        )

        ending_days_offset = self.interval_to_params[interval]["ending_days_offset"]

        current_time = datetime.now(UTC)
        cutoff_date = current_time - timedelta(days=ending_days_offset)
        start_date = current_time - timedelta(days=chart_length)

        source_ohlcv = current_coin_historical_ohlcv[
            (current_coin_historical_ohlcv["datetime"] > str(start_date))
        ]

        combined_ohlcv = pd.concat(
            [og_coins_historical_ohlcvs, current_coin_historical_ohlcv]
        )
        combined_ohlcv = combined_ohlcv[
            (combined_ohlcv["datetime"] <= str(cutoff_date))
        ]

        all_matches = []
        allowed_day_difference = self.interval_to_params[interval][
            "allowed_day_difference"
        ]

        for coin in self.og_coins_for_flashback:
            coin_ohlcv = combined_ohlcv[combined_ohlcv["coin"] == coin]
            coin_dates = pd.to_datetime(coin_ohlcv["datetime"]).values

            matches = _find_similar_pattern(
                source_ohlcv["close"].values,
                coin_ohlcv["close"].values,
            )
            coin_matche_dates = []

            for match_dist, match_idx in matches:
                match_date = coin_dates[match_idx]

                is_too_close = False
                for existing_match_date in coin_matche_dates:
                    days_diff = abs(
                        (match_date - existing_match_date) / np.timedelta64(1, "D")
                    )
                    if days_diff < allowed_day_difference:
                        is_too_close = True
                        break

                if not is_too_close:
                    coin_matche_dates.append(coin_dates[match_idx])

                    match_coin_data = coin_ohlcv.iloc[
                        match_idx : match_idx + number_of_points + 20
                    ][["datetime", "open", "high", "low", "close", "volume"]]

                    all_matches.append(
                        {
                            "coin": coin,
                            "distance": float(match_dist),
                            "start_time": match_coin_data.iloc[0]["datetime"],
                            "end_time": match_coin_data.iloc[-1]["datetime"],
                            "label": f"{coin}_{pd.Timestamp(match_date).strftime('%Y-%m-%d %H:%M:%S')}_{match_coin_data.iloc[-1]['datetime']}",
                        }
                    )

        sorted_results = sorted(all_matches, key=lambda x: x["distance"])[:10]

        return {
            "type": "flashback_coins",
            "coin_name": coin_name,
            "interval": interval,
            "start_time": source_ohlcv.iloc[0]["datetime"],
            "end_time": source_ohlcv.iloc[-1]["datetime"],
            "following_points_number": 20,
            "flashback_coins": [match for match in sorted_results],
        }
