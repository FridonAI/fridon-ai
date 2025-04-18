from datetime import datetime
from typing import List, Dict, Any, Union, Literal
import pandas as pd
from libs.data_providers.ohlcv.base import BaseOHLCVProvider
from libs.data_providers.ohlcv.birdeye import BirdeyeOHLCVProvider


class CompositeCoinDataProvider:
    """
    Composite implementation of the coin price data provider.
    Combines multiple providers and tries them in order.
    """

    def __init__(self, ohlcv_providers: list[BaseOHLCVProvider]):
        self.ohlcv_providers = ohlcv_providers

    async def get_current_ohlcv(
        self,
        symbols: List[str],
        interval: str,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: List[Literal["spot", "futures"]] = ["spot", "futures"],
    ) -> List[Dict[str, Any]]:
        if not symbols:
            return []
        remaining_symbols = symbols.copy()
        results = []
        for cat in category:
            for provider in self.ohlcv_providers:
                if not remaining_symbols:
                    break
                resp = await provider.get_current_ohlcv(
                    remaining_symbols, interval, output_format, cat
                )
                if isinstance(resp, tuple) or len(resp) > 0:
                    results.append(resp)
                    fetched_symbols = list(
                        set(item.get("coin") for item in resp if "coin" in item)
                    )
                    remaining_symbols = [
                        s for s in remaining_symbols if s not in fetched_symbols
                    ]
            if not remaining_symbols:
                break
        if not results:
            return []
        combined = []
        for r in results:
            combined.extend(r)
        return combined

    def _is_address(self, symbol: str) -> bool:
        return len(symbol) > 30

    async def get_historical_ohlcv(
        self,
        symbols: List[str],
        interval: str,
        days: int,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: List[Literal["spot", "futures"]] = ["spot", "futures"],
    ):
        if not symbols:
            return []
        remaining_symbols = []
        results = []

        for symbol in symbols:
            if self._is_address(symbol):
                resp = await self.get_historical_ohlcv_for_address(
                    address=symbol,
                    interval=interval,
                    days=days,
                    output_format=output_format,
                )
                if isinstance(resp, tuple) or len(resp) > 0:
                    results.append(resp)
            else:
                remaining_symbols.append(symbol)
        for cat in category:
            for provider in self.ohlcv_providers:
                if not remaining_symbols:
                    break
                resp = await provider.get_historical_ohlcv(
                    remaining_symbols, interval, days, output_format, cat
                )
                if isinstance(resp, tuple) or len(resp) > 0:
                    results.append(resp)
                    if isinstance(resp, pd.DataFrame):
                        fetched_symbols = (
                            resp["coin"].unique().tolist()
                            if "coin" in resp.columns
                            else []
                        )
                    else:
                        fetched_symbols = list(
                            set(item.get("coin") for item in resp if "coin" in item)
                        )
                    remaining_symbols = [
                        s for s in remaining_symbols if s not in fetched_symbols
                    ]
            if not remaining_symbols:
                break
        if not results:
            return []
        if isinstance(results[0], pd.DataFrame):
            return pd.concat(results)
        combined = []
        for r in results:
            combined.extend(r)
        return combined

    async def get_historical_ohlcv_by_start_end(
        self,
        symbols: List[str],
        interval: str,
        start_time: datetime,
        end_time: datetime,
        output_format: Literal["dataframe", "dict"] = "dataframe",
        category: List[Literal["spot", "futures"]] = ["spot", "futures"],
    ):
        if not symbols:
            return []
        remaining_symbols = []
        results = []
        for symbol in symbols:
            if self._is_address(symbol):
                resp = await self.get_historical_ohlcv_by_start_end_for_address(
                    address=symbol,
                    interval=interval,
                    start_time=start_time,
                    end_time=end_time,
                    output_format=output_format,
                )
                if isinstance(resp, tuple) or len(resp) > 0:
                    results.append(resp)
            else:
                remaining_symbols.append(symbol)
        for cat in category:
            for provider in self.ohlcv_providers:
                if not remaining_symbols:
                    break
                resp = await provider.get_historical_ohlcv_by_start_end(
                    remaining_symbols,
                    interval,
                    start_time,
                    end_time,
                    output_format,
                    cat,
                )
                if isinstance(resp, tuple) or len(resp) > 0:
                    results.append(resp)
                    if isinstance(resp, pd.DataFrame):
                        fetched_symbols = (
                            resp["coin"].unique().tolist()
                            if "coin" in resp.columns
                            else []
                        )
                    else:
                        fetched_symbols = list(
                            set(item.get("coin") for item in resp if "coin" in item)
                        )
                    remaining_symbols = [
                        s for s in remaining_symbols if s not in fetched_symbols
                    ]
            if not remaining_symbols:
                break
        if not results:
            return []
        if isinstance(results[0], pd.DataFrame):
            return pd.concat(results)
        combined = []
        for r in results:
            combined.extend(r)
        return combined

    async def get_historical_ohlcv_by_start_end_for_address(
        self,
        address: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ):
        for provider in self.ohlcv_providers:
            if isinstance(provider, BirdeyeOHLCVProvider):
                return await provider.get_historical_ohlcv_by_start_end_for_address(
                    address,
                    interval,
                    start_time,
                    end_time,
                    output_format,
                )
        print("No birdeye provider found")
        return []

    async def get_historical_ohlcv_for_address(
        self,
        address: str,
        interval: str,
        days: int,
        output_format: Literal["dataframe", "dict"] = "dataframe",
    ):
        for provider in self.ohlcv_providers:
            if isinstance(provider, BirdeyeOHLCVProvider):
                return await provider.get_historical_ohlcv_for_address(
                    address, interval, days, output_format
                )
        print("No birdeye provider found")
        return []

    async def _get_ca_symbol_birdeye(self, address: str) -> str:
        for provider in self.ohlcv_providers:
            if isinstance(provider, BirdeyeOHLCVProvider):
                return await provider._get_ca_symbol_birdeye(address)
        return address
