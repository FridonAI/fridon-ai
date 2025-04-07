import requests
import time
import datetime
import os
from typing import Optional, Dict, Any, Literal

from libs.data_providers.derivative.base import DerivativeDataProvider

import pandas as pd

from settings import settings


class CoinalyzeDataProvider(DerivativeDataProvider):
    BASE_URL = "https://api.coinalyze.net/v1"
    RATE_LIMIT = 40

    interval_to_days: dict[Literal["1h", "4h", "1d", "1w"], dict] = {
        "30min": 4,
        "1hour": 7,
        "4hour": 28,
        "daily": 100,
    }

    def __init__(self, api_key: str | None = None):
        self.headers = {"api_key": api_key or settings.COINALYZE_API_KEY}
        self.last_request_time = 0

    def _rate_limit(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_request_time
        if elapsed_time < 1.5:  # Ensure we don't exceed rate limit
            time.sleep(1.5 - elapsed_time)
        self.last_request_time = time.time()

    def _fetch_data(self, endpoint: str, params: dict) -> Dict[str, Any]:
        """
        Generic method to fetch data from Coinalyze API
        """
        self._rate_limit()
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_supported_exchanges(self) -> pd.DataFrame:
        """
        Get list of supported exchanges
        """
        data = self._fetch_data("exchanges", {})
        return pd.DataFrame(data)

    def get_supported_future_markets(self) -> pd.DataFrame:
        """
        Get list of supported future markets
        """
        data = self._fetch_data("future-markets", {})
        return pd.DataFrame(data)

    def get_supported_spot_markets(self) -> pd.DataFrame:
        """
        Get list of supported spot markets
        """
        data = self._fetch_data("spot-markets", {})
        return pd.DataFrame(data)

    def get_open_interest(self, symbol: str) -> pd.DataFrame:
        """
        Get current open interest for a symbol
        """
        data = self._fetch_data("open-interest", {"symbols": symbol})
        return pd.DataFrame(data)

    def get_open_interest_history(
        self,
        symbol: str,
        interval: str = "1hour",
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        days: int = None,
        convert_to_usd: bool = False,
    ) -> pd.DataFrame:
        """
        Get historical open interest data

        Args:
            symbol: Trading pair symbol
            interval: Time interval (1min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 12hour, daily)
            from_timestamp: Start time in UNIX timestamp (seconds)
            to_timestamp: End time in UNIX timestamp (seconds)
            convert_to_usd: Whether to convert values to USD

        Returns:
            DataFrame with open interest history
        """
        if from_timestamp is None:
            from_timestamp = int(
                (
                    datetime.datetime.now()
                    - datetime.timedelta(days=days or self.interval_to_days[interval])
                ).timestamp()
            )
        if to_timestamp is None:
            to_timestamp = int(datetime.datetime.now().timestamp())

        params = {
            "symbols": symbol,
            "interval": interval,
            "from": from_timestamp,
            "to": to_timestamp,
            "convert_to_usd": str(convert_to_usd).lower(),
        }

        data = self._fetch_data("open-interest-history", params)

        result_data = []
        for item in data:
            symbol = item["symbol"]
            for history_item in item["history"]:
                row = {
                    "symbol": symbol,
                    "timestamp": history_item["t"] * 1000,
                    "open_interest": history_item["c"],
                    "open": history_item["o"],
                    "high": history_item["h"],
                    "low": history_item["l"],
                    "close": history_item["c"],
                }
                result_data.append(row)

        return pd.DataFrame(result_data)

    def get_funding_rates(self, symbol: str) -> pd.DataFrame:
        """
        Get current funding rates for a symbol
        """
        data = self._fetch_data("funding-rate", {"symbols": symbol})
        return pd.DataFrame(data)

    def get_funding_rate_history(
        self,
        symbol: str,
        interval: str = "1hour",
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        days: int = None,
    ) -> pd.DataFrame:
        """
        Get historical funding rate data

        Args:
            symbol: Trading pair symbol
            interval: Time interval (1min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 12hour, daily)
            from_timestamp: Start time in UNIX timestamp (seconds)
            to_timestamp: End time in UNIX timestamp (seconds)

        Returns:
            DataFrame with funding rate history
        """
        if from_timestamp is None:
            from_timestamp = int(
                (
                    datetime.datetime.now()
                    - datetime.timedelta(days=days or self.interval_to_days[interval])
                ).timestamp()
            )
        if to_timestamp is None:
            to_timestamp = int(datetime.datetime.now().timestamp())

        params = {
            "symbols": symbol,
            "interval": interval,
            "from": from_timestamp,
            "to": to_timestamp,
        }

        data = self._fetch_data("funding-rate-history", params)

        result_data = []
        for item in data:
            symbol = item["symbol"]
            for history_item in item["history"]:
                row = {
                    "symbol": symbol,
                    "timestamp": history_item["t"] * 1000,
                    "funding_rate": history_item["c"],  # Using close value
                    "open": history_item["o"],
                    "high": history_item["h"],
                    "low": history_item["l"],
                    "close": history_item["c"],
                }
                result_data.append(row)

        return pd.DataFrame(result_data)

    def get_liquidations(self, symbol: str) -> pd.DataFrame:
        """
        Get current liquidations for a symbol
        """
        data = self._fetch_data("liquidations", {"symbols": symbol})
        return pd.DataFrame(data)

    def get_liquidation_history(
        self,
        symbol: str,
        interval: str = "1hour",
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        days: int = None,
        convert_to_usd: bool = True,
    ) -> pd.DataFrame:
        """
        Get historical liquidation data

        Args:
            symbol: Trading pair symbol
            interval: Time interval (1min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 12hour, daily)
            from_timestamp: Start time in UNIX timestamp (seconds)
            to_timestamp: End time in UNIX timestamp (seconds)
            convert_to_usd: Whether to convert values to USD

        Returns:
            DataFrame with liquidation history
        """
        if from_timestamp is None:
            from_timestamp = int(
                (
                    datetime.datetime.now()
                    - datetime.timedelta(days=days or self.interval_to_days[interval])
                ).timestamp()
            )
        if to_timestamp is None:
            to_timestamp = int(datetime.datetime.now().timestamp())

        params = {
            "symbols": symbol,
            "interval": interval,
            "from": from_timestamp,
            "to": to_timestamp,
            "convert_to_usd": str(convert_to_usd).lower(),
        }

        data = self._fetch_data("liquidation-history", params)

        result_data = []
        for item in data:
            symbol = item["symbol"]
            for history_item in item["history"]:
                row = {
                    "symbol": symbol,
                    "timestamp": history_item["t"] * 1000,
                    "long_liquidations": history_item["l"],  # Long liquidations
                    "short_liquidations": history_item["s"],
                    "liquidation_volume": history_item["l"] + history_item["s"],
                    "side": "long"
                    if history_item["l"] > history_item["s"]
                    else "short",
                }
                result_data.append(row)

        return pd.DataFrame(result_data)

    def get_long_short_ratio(self, symbol: str) -> pd.DataFrame:
        """
        Get current long/short ratio for a symbol
        """
        data = self._fetch_data("long-short-ratio", {"symbols": symbol})
        return pd.DataFrame(data)

    def get_long_short_ratio_history(
        self,
        symbol: str,
        interval: str = "1hour",
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        days: int = None,
    ):
        """
        Get historical long/short ratio data for a symbol

        Args:
            symbol: Trading pair symbol
            interval: Time interval (1min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 12hour, daily)
            from_timestamp: Start time in UNIX timestamp (seconds)
            to_timestamp: End time in UNIX timestamp (seconds)

        Returns:
            DataFrame with long/short ratio history
        """
        if from_timestamp is None:
            from_timestamp = int(
                (
                    datetime.datetime.now()
                    - datetime.timedelta(days=days or self.interval_to_days[interval])
                ).timestamp()
            )
        if to_timestamp is None:
            to_timestamp = int(datetime.datetime.now().timestamp())

        params = {
            "symbols": symbol,
            "interval": interval,
            "from": from_timestamp,
            "to": to_timestamp,
        }

        data = self._fetch_data("long-short-ratio-history", params)

        result_data = []
        for item in data:
            symbol = item["symbol"]
            for history_item in item["history"]:
                row = {
                    "symbol": symbol,
                    "timestamp": history_item["t"] * 1000,
                    "long_short_ratio": history_item["r"],
                    "longs": history_item["l"],
                    "shorts": history_item["s"],
                }
                result_data.append(row)

        return pd.DataFrame(result_data)

    def get_basis(self, symbol: str):
        params = {"symbols": symbol}
        data = self._fetch_data("basis", params)
        return data

    def get_consolidated_data(
        self,
        symbol: str,
        interval: str = "1hour",
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        days: int = None,
        include_oi: bool = True,
        include_funding: bool = True,
        include_liquidations: bool = True,
        include_ls_ratio: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetches multiple data types and aligns them by timestamp for easier analysis.

        Parameters:
            symbol: Trading pair symbol
            interval: Time interval
            from_timestamp: Start time in UNIX timestamp (seconds)
            to_timestamp: End time in UNIX timestamp (seconds)
            include_oi: Whether to include open interest data
            include_funding: Whether to include funding rate data
            include_liquidations: Whether to include liquidation data
            include_ls_ratio: Whether to include long/short ratio data

        Returns:
            Dict containing DataFrames for each data type and a merged DataFrame
        """
        result = {}

        if from_timestamp is None:
            from_timestamp = int(
                (
                    datetime.datetime.now()
                    - datetime.timedelta(days=days or self.interval_to_days[interval])
                ).timestamp()
            )
        if to_timestamp is None:
            to_timestamp = int(datetime.datetime.now().timestamp())

        if include_oi:
            oi_df = self.get_open_interest_history(
                symbol=symbol,
                interval=interval,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
            )
            result["open_interest"] = oi_df

        if include_funding:
            funding_df = self.get_funding_rate_history(
                symbol=symbol,
                interval=interval,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
            )
            result["funding"] = funding_df

        if include_liquidations:
            liquidation_df = self.get_liquidation_history(
                symbol=symbol,
                interval=interval,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
            )
            result["liquidations"] = liquidation_df

        if include_ls_ratio:
            ls_ratio_df = self.get_long_short_ratio_history(
                symbol=symbol,
                interval=interval,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
            )
            result["long_short_ratio"] = ls_ratio_df

        merged_df = None

        if include_oi:
            merged_df = oi_df[["timestamp", "symbol", "open_interest"]].copy()

        if include_funding and merged_df is not None:
            merged_df = pd.merge_asof(
                merged_df,
                funding_df[["timestamp", "funding_rate"]],
                on="timestamp",
                direction="nearest",
            )
        elif include_funding:
            merged_df = funding_df.copy()

        if include_liquidations and merged_df is not None:
            liq_agg = liquidation_df[
                ["timestamp", "long_liquidations", "short_liquidations"]
            ].copy()

            liq_agg.rename(
                columns={"long_liquidations": "long", "short_liquidations": "short"},
                inplace=True,
            )

            liq_agg = (
                liq_agg.groupby("timestamp")
                .agg({"long": "sum", "short": "sum"})
                .reset_index()
            )

            merged_df = pd.merge_asof(
                merged_df, liq_agg, on="timestamp", direction="nearest"
            )
        elif include_liquidations:
            merged_df = liquidation_df.copy()

        if include_ls_ratio and merged_df is not None:
            merged_df = pd.merge_asof(
                merged_df,
                ls_ratio_df[["timestamp", "long_short_ratio"]],
                on="timestamp",
                direction="nearest",
            )
        elif include_ls_ratio:
            merged_df = ls_ratio_df.copy()

        if merged_df is not None:
            result["merged"] = merged_df

        return result

    def _to_coinalyze_interval(self, interval: str) -> str:
        return {
            "30m": "30min",
            "1h": "1hour",
            "4h": "4hour",
            "1d": "daily",
        }[interval]

    def _to_coinalyze_symbol_name(self, symbol: str) -> str:
        if not symbol.endswith("USDT_PERP.A"):
            return f"{symbol.upper()}USDT_PERP.A"
        return symbol
