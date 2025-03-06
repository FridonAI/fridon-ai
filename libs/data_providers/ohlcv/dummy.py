import pandas as pd
import random
from datetime import datetime, timedelta
from typing import List, Literal, Union, Dict, Any

from libs.data_providers.ohlcv.base import BaseOHLCVProvider


class DummyOHLCVProvider(BaseOHLCVProvider):
    """
    Dummy implementation of the coin price data provider.
    Generates random data for testing.
    """

    async def get_historical_ohlcv(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        days: int = 30,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ) -> Union[pd.DataFrame, pl.DataFrame, List[Dict[str, Any]]]:
        """
        Generate random OHLCV data for a list of symbols.
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        return await self.get_historical_ohlcv_by_start_end(
            symbols, interval, start_time, end_time, output_format
        )

    async def get_historical_ohlcv_by_start_end(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        start_time: datetime,
        end_time: datetime,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Generate random OHLCV data for a list of symbols within a specific time range.
        """
        interval_hours = {"1h": 1, "4h": 4, "1d": 24, "1w": 168}
        hours_diff = (end_time - start_time).total_seconds() / 3600
        num_intervals = int(hours_diff / interval_hours[interval])

        all_data = []

        for symbol in symbols:
            price = random.uniform(10, 1000)

            for i in range(num_intervals):
                timestamp = start_time + timedelta(hours=i * interval_hours[interval])
                timestamp_ms = int(timestamp.timestamp() * 1000)

                change = random.uniform(-0.05, 0.05)
                close = price * (1 + change)
                high = max(price, close) * (1 + random.uniform(0, 0.03))
                low = min(price, close) * (1 - random.uniform(0, 0.03))
                volume = random.uniform(10000, 1000000)

                all_data.append(
                    {
                        "coin": symbol,
                        "timestamp": timestamp_ms,
                        "open": price,
                        "high": high,
                        "low": low,
                        "close": close,
                        "volume": volume,
                    }
                )
                price = close

        if output_format == "dict":
            return all_data
        elif output_format == "dataframe":
            if len(all_data) == 0:
                return pd.DataFrame()
            return pd.DataFrame(all_data)

    async def get_historical_ohlcv_for_address(
        self,
        address: str,
        interval: Literal["1h", "4h", "1d", "1w"],
        days: int = 30,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ) -> Union[pd.DataFrame, pl.DataFrame, List[Dict[str, Any]]]:
        """
        Generate random OHLCV data for a specific token address.
        """
        return await self.get_historical_ohlcv(
            [address[:5]], interval, days, output_format
        )

    async def get_historical_ohlcv_by_start_end_for_address(
        self,
        address: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        start_time: datetime,
        end_time: datetime,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Generate random OHLCV data for a specific token address within a time range.
        """
        symbols = [addr[:5] for addr in address]
        return await self.get_historical_ohlcv_by_start_end(
            symbols, interval, start_time, end_time, output_format
        )

    async def get_current_price(self, symbols: List[str]) -> Dict[str, float]:
        """
        Generate random current prices for a list of symbols.
        """
        return {symbol: random.uniform(10, 1000) for symbol in symbols}
