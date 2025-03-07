from typing import List, Literal, Union, Dict, Any
from datetime import datetime
import pandas as pd
import asyncio


class BaseOHLCVProvider:
    """
    Abstract base class for fetching OHLCV (Open, High, Low, Close, Volume) data.
    Implementations should provide methods to fetch OHLCV data for crypto tokens.
    """

    _batch_size = ...
    _request_delay = ...

    async def get_historical_ohlcv(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        days: int = 30,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: Literal["spot", "futures"] = "spot",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Fetch historical OHLCV data for a list of symbols.

        Args:
            symbo of coin ls: Listsymbols
            interval: Time interval for the data (1h, 4h, 1d, 1w)
            days: Number of days of historical data to fetch
            output_format: Format of the output data (dataframe or dict)

        Returns:
            Historical OHLCV data in the specified format
        """
        ...

    async def get_historical_ohlcv_by_start_end(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        start_time: datetime,
        end_time: datetime,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: Literal["spot", "futures"] = "spot",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Fetch historical OHLCV data for a list of symbols within a specific time range.

        Args:
            symbols: List of coin symbols
            interval: Time interval for the data (1h, 4h, 1d, 1w)
            start_time: Start time for fetching data
            end_time: End time for fetching data
            output_format: Format of the output data (dataframe or dict)

        Returns:
            Historical OHLCV data in the specified format
        """
        ...

    async def get_historical_ohlcv_for_address(
        self,
        address: str,
        interval: Literal["1h", "4h", "1d", "1w"],
        days: int = 30,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: Literal["spot", "futures"] = "spot",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Fetch historical OHLCV data for a specific token address.

        Args:
            address: Token contract address
            interval: Time interval for the data (1h, 4h, 1d, 1w)
            days: Number of days of historical data to fetch
            output_format: Format of the output data (dataframe or dict)

        Returns:
            Historical OHLCV data in the specified format
        """
        pass

    async def get_historical_ohlcv_by_start_end_for_address(
        self,
        address: str,
        interval: Literal["1h", "4h", "1d", "1w"],
        start_time: datetime,
        end_time: datetime,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: Literal["spot", "futures"] = "spot",
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Fetch historical OHLCV data for a token address within a specific time range.

        Args:
            address: Token contract address
            interval: Time interval for the data (1h, 4h, 1d, 1w)
            start_time: Start time for fetching data
            end_time: End time for fetching data
            output_format: Format of the output data (dataframe or dict)

        Returns:
            Historical OHLCV data in the specified format
        """
        ...

    async def get_current_ohlcv(
        self,
        symbols: List[str],
        interval: Literal["1h", "4h", "1d", "1w"],
        category: Literal["spot", "futures"] = "spot",
    ) -> List[Dict[str, Any]]:
        """
        Fetch current OHLCV data for a list of symbols.

        Args:
            symbols: List of coin symbols
            interval: Time interval for the data (1h, 4h, 1d, 1w)

        Returns:
            Dictionary mapping symbols to their current OHLCV data
        """
        ...

    async def _execute_in_batches(self, tasks: list[asyncio.Future]) -> List:
        results = []
        for i in range(0, len(tasks), self._batch_size):
            batch = tasks[i : i + self._batch_size]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)
            if i + self._batch_size < len(tasks):
                await asyncio.sleep(self._request_delay)
        return results

    def _to_dataframe(self, data: list[dict]) -> pd.DataFrame:
        if not data:
            return pd.DataFrame()
        columns = [
            "coin",
            "timestamp",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        df = pd.DataFrame(data, columns=columns)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df