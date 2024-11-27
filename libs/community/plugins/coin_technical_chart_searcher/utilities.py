import requests
from datetime import UTC, datetime, timedelta
from typing import List, Literal, Tuple, Union

import stumpy
import numpy as np
import pandas as pd


from fridonai_core.plugins.utilities import BaseUtility
from libs.community.plugins.coin_technical_analyzer.helpers.llm import get_filter_generator_chain
from libs.data_providers.coin_price_providers import BinanceCoinPriceDataProvider
from libs.repositories.indicators import IndicatorsRepository
from settings import settings


class CoinPriceChartSimilaritySearchUtility(BaseUtility):
    async def arun(
        self, coin_name: str, start_date: str | None = None, *args, **kwargs
    ) -> str | dict:
        if start_date is not None:
            start_date = datetime.fromisoformat(start_date)
            end_date = min(start_date + timedelta(days=30), datetime.now())
        else:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

        req = {
            "coin": coin_name.upper(),
            "from": int(start_date.timestamp() * 1000),
            "to": int(end_date.timestamp() * 1000),
            "topK": 3,
        }

        resp = requests.post(
            settings.API_URL + "/blockchain/coin-similarity", json=req
        ).json()

        if "statusCode" in resp:
            if 500 > resp["statusCode"] >= 400:
                return resp.get("message", "Something went wrong!")
            if resp["statusCode"] >= 500:
                return "Something went wrong! Please try again later."

        return  {
            "type": "similar_coins",
            "coin": coin_name,
            "start_date_timestamp": int(start_date.timestamp()),
            "end_date_timestamp": int(end_date.timestamp()),
            "start_date": start_date.strftime("%d %B %Y"),
            "end_date": end_date.strftime("%d %B %Y"),
            **resp,
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
            eval(filter_expression)
        )

        if len(latest_records) == 0:
            return "No coins found"

        return latest_records.to_dicts()


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

    def _get_plot_data(
        self, ohlcv: pd.DataFrame, start_idx: int, end_idx: int
    ) -> pd.DataFrame:
        plot_data = ohlcv.iloc[start_idx:end_idx][
            ["datetime", "open", "high", "low", "close", "volume"]
        ]
        plot_data.columns = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
        plot_data.set_index(pd.to_datetime(plot_data["Date"]), inplace=True)
        plot_data.drop(columns=["Date"], inplace=True)
        return plot_data

    def _find_similar_pattern(
        self,
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

    async def arun(
        self,
        coin_name: str,
        interval: Literal["1h", "4h", "1d", "1w"] = "1d",
        *args,
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

            matches = self._find_similar_pattern(
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

                    match_coin_plot_data = self._get_plot_data(
                        coin_ohlcv, match_idx, match_idx + number_of_points + 20
                    )

                    all_matches.append(
                        {
                            "coin": coin,
                            "index": match_idx,
                            "distance": match_dist,
                            "date": str(match_date),
                            "label": f"{coin}_{pd.Timestamp(match_date).strftime('%Y-%m-%d')}_{match_coin_plot_data.index[-1].strftime('%Y-%m-%d')}",
                        }
                    )

        sorted_results = sorted(all_matches, key=lambda x: x["distance"])[:10]

        resp = [
            {
                "label": match["label"],
                "distance": match["distance"],
                "start_date": match["date"],
            }
            for match in sorted_results
        ]

        return {
            "type": "flashback_coins",
            "coin_name": coin_name,
            "interval": interval,
            "chart_length": chart_length,
            "following_points_number": number_of_points,
            "flashback_coins": resp,
        }
