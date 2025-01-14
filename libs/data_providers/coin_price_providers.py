import asyncio
import os
import random
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path

import aiohttp
import pandas as pd

from libs.data_providers.token_providers import JupiterTokenListDataProvider


class CoinPriceDataProvider:
    async def get_current_ohlcv(self, coins, interval, output_format): ...

    async def get_historical_ohlcv(self, coins, interval, days, output_format): ...


class DummyCoinPriceDataProvider(CoinPriceDataProvider):
    async def get_current_ohlcv(self, coins, interval="30m", output_format="dict"):
        return self._generate_coin_price_data_mock(coins)

    async def get_historical_ohlcv(
        self, coins, interval="30m", days=45, output_format="dict"
    ):
        print("Dummy data not implemented for historical ohlcv")
        pass

    def _generate_coin_price_data_mock(self, coins, current_time=None):
        data = []
        if current_time is None:
            current_time = datetime.now(UTC).replace(microsecond=0)
        timestamp = int(current_time.timestamp() * 1000)
        date_str = current_time.strftime("%Y-%m-%d")
        for coin in coins:
            open_price = random.uniform(1000, 50000)
            close_price = open_price + random.uniform(-500, 500)
            high_price = max(open_price, close_price) + random.uniform(0, 500)
            low_price = min(open_price, close_price) - random.uniform(0, 500)
            volume = random.uniform(100, 10000)
            data.append(
                {
                    "coin": coin,
                    "timestamp": timestamp,
                    "date": date_str,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                }
            )
        return data, current_time


class BinanceCoinPriceDataProvider(CoinPriceDataProvider):
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"

    async def get_current_ohlcv(self, coins, interval="30m", output_format="dict"):
        return await self._generate_coins_price_data_binance(
            coins, interval, output_format=output_format
        )

    async def get_historical_ohlcv(
        self, coins, interval="30m", days=45, output_format="dict"
    ):
        return await self._generate_historical_coins_price_data_binance(
            coins, interval, days, output_format=output_format
        )

    async def get_historical_ohlcv_by_start_end(
        self, coins, interval, start_time, end_time, output_format="dataframe"
    ):
        return await self._generate_multiple_coins_price_data(
            coins,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            output_format=output_format,
        )

    async def _fetch_coin_ohlcv_binance(
        self, symbol, interval, days=None, limit=1, start_time=None, end_time=None
    ):
        formatted_data = []

        if days is not None or (start_time is not None and end_time is not None):
            if start_time is None:
                start_time = int(
                    (datetime.now(UTC) - timedelta(days=days)).timestamp() * 1000
                )

            while True:
                url = f"{self.base_url}?symbol={symbol}USDT&interval={interval}&startTime={start_time}&limit=500"
                if end_time:
                    url += f"&endTime={end_time}"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            data = await resp.json()
                            if "code" in data and data["code"] in [-1121, -1100]:
                                return []
                except Exception as e:
                    print(f"Error fetching {symbol} {interval} data from Binance: {e}")
                    return []

                if not data:
                    break

                for entry in data:
                    timestamp = int(entry[0])
                    date_str = datetime.fromtimestamp(timestamp // 1000).strftime(
                        "%Y-%m-%d"
                    )
                    formatted_data.append(
                        {
                            "coin": symbol,
                            "timestamp": timestamp,
                            "date": date_str,
                            "open": float(entry[1]),
                            "high": float(entry[2]),
                            "low": float(entry[3]),
                            "close": float(entry[4]),
                            "volume": float(entry[5]),
                        }
                    )

                if len(data) < 500:
                    break

                start_time = data[-1][0] + 1
                await asyncio.sleep(0.1)

        else:
            url = f"{self.base_url}?symbol={symbol}USDT&interval={interval}&endTime={end_time}&limit={limit}"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        data = await resp.json()
                        if "code" in data and data["code"] in [-1121, -1100]:
                            return []
            except Exception as e:
                print(f"Error fetching {symbol} {interval} data from Binance: {e}")
                return []

            for entry in data:
                timestamp = int(entry[0])
                date_str = datetime.fromtimestamp(timestamp // 1000).strftime(
                    "%Y-%m-%d"
                )
                formatted_data.append(
                    {
                        "coin": symbol,
                        "timestamp": timestamp,
                        "date": date_str,
                        "open": float(entry[1]),
                        "high": float(entry[2]),
                        "low": float(entry[3]),
                        "close": float(entry[4]),
                        "volume": float(entry[5]),
                    }
                )

        return formatted_data

    async def _generate_multiple_coins_price_data(
        self,
        coins,
        interval="30m",
        days=None,
        batch_size=10,
        output_format="dict",
        start_time=None,
        end_time=None,
    ):
        data = []
        tasks = []
        now = datetime.now(UTC)

        if start_time is not None and end_time is not None:
            start_time = int(start_time.timestamp() * 1000)
            end_time = int(end_time.timestamp() * 1000)
        else:
            if now.minute >= 30:
                end_time = now.replace(minute=30, second=0, microsecond=0)
            else:
                end_time = now.replace(minute=0, second=0, microsecond=0)
            end_time = int(end_time.timestamp() * 1000) - 1
            readable_end_time = datetime.fromtimestamp(end_time / 1000, UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print(f"Fetching latest coin prices before {readable_end_time}")
        for i, symbol in enumerate(coins):
            tasks.append(
                self._fetch_coin_ohlcv_binance(
                    symbol,
                    interval,
                    days=days,
                    start_time=start_time,
                    end_time=end_time,
                )
            )
            if (i + 1) % batch_size == 0:
                result = await asyncio.gather(*tasks)
                for coin_data in result:
                    data.extend(coin_data)
                tasks = []
                await asyncio.sleep(0.1)

        if tasks:
            result = await asyncio.gather(*tasks)
            for coin_data in result:
                data.extend(coin_data)

        if output_format == "dataframe":
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
            df = pd.DataFrame.from_records(data, columns=columns)
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)

            return df

        return data, datetime.now(UTC).replace(microsecond=0)

    async def _generate_coins_price_data_binance(
        self, coins, interval="30m", output_format="dict"
    ):
        return await self._generate_multiple_coins_price_data(
            coins, interval, output_format=output_format
        )

    async def _generate_historical_coins_price_data_binance(
        self, coins, interval="30m", days=45, output_format="dict"
    ):
        return await self._generate_multiple_coins_price_data(
            coins, interval, days=days, batch_size=5, output_format=output_format
        )

class BirdeyeCoinPriceDataProvider(CoinPriceDataProvider):
    CACHE_DIR = Path("../../cache")
    CACHE_FILE = CACHE_DIR / "token_list_cache.json"
    CACHE_DURATION = timedelta(days=1)

    def __init__(self, token_list):
        self._base_url = "https://public-api.birdeye.so"
        self._birdeye_api_key = os.getenv("BIRDEYE_API_KEY")
        self._token_map = {
            token["symbol"].upper().lstrip("$"): token for token in token_list
        }
        self._interval_map = {
            "30m": "30m",
            "1h": "1H",
            "4h": "4H",
            "1d": "1D",
            "1w": "1W",
        }

    @staticmethod
    async def create():
        token_list = await BirdeyeCoinPriceDataProvider._get_cached_token_list()
        return BirdeyeCoinPriceDataProvider(token_list)

    @staticmethod
    async def _get_cached_token_list():
        # Create cache directory if it doesn't exist
        BirdeyeCoinPriceDataProvider.CACHE_DIR.mkdir(exist_ok=True)

        # Check if cache file exists and is fresh
        if BirdeyeCoinPriceDataProvider.CACHE_FILE.exists():
            with open(BirdeyeCoinPriceDataProvider.CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                cache_time = datetime.fromtimestamp(cache_data["timestamp"], UTC)

                # If cache is fresh, return cached data
                if (
                    datetime.now(UTC) - cache_time
                    < BirdeyeCoinPriceDataProvider.CACHE_DURATION
                ):
                    return cache_data["token_list"]

        # If cache doesn't exist or is stale, fetch new data
        token_list_provider = JupiterTokenListDataProvider()
        token_list = await token_list_provider.get_token_list()

        # Save to cache
        cache_data = {
            "timestamp": datetime.now(UTC).timestamp(),
            "token_list": token_list,
        }
        with open(BirdeyeCoinPriceDataProvider.CACHE_FILE, "w") as f:
            json.dump(cache_data, f)

        return token_list

    async def get_current_ohlcv(self, coins, interval: str = "30m", output_format: str = "dict"):
        interval = self._interval_map[interval]
        data = []
        tasks = []
        for symbol in coins:
            symbol = symbol.upper()
            params = {
                "symbol": symbol,
                "address": self._token_map[symbol]["address"],
                "type": interval,
                "time_from": int((datetime.now(UTC) - timedelta(days=1)).timestamp()),
                "time_to": int(datetime.now(UTC).timestamp()),
            }
            tasks.append(self._fetch_coin_ohlcv_birdeye(params))

            if len(tasks) >= 15:
                batch_results = await asyncio.gather(*tasks)
                for coin_result in batch_results:
                    data.extend(coin_result[-1:0])
                tasks = []
                await asyncio.sleep(1)
        # Process any remaining tasks
        if tasks:
            batch_results = await asyncio.gather(*tasks)
            for coin_result in batch_results:
                data.extend(coin_result[-1:])

        return data, datetime.now(UTC).replace(microsecond=0)


    async def get_historical_ohlcv(self, coins, interval: str = "30m", days: int = 45, output_format: str = "dict"):
        interval = self._interval_map[interval]
        data = []
        tasks = []
        for symbol in coins:
            symbol = symbol.upper()
            params = {
                "symbol": symbol,
                "address": self._token_map[symbol]["address"],
                "type": interval,
                "time_from": int((datetime.now(UTC) - timedelta(days=days)).timestamp()),
                "time_to": int(datetime.now(UTC).timestamp()),
            }
            tasks.append(self._fetch_coin_ohlcv_birdeye(params))

            # Process in batches of 15 requests per second
            if len(tasks) >= 15:
                batch_results = await asyncio.gather(*tasks)
                for coin_result in batch_results:
                    data.extend(coin_result)
                tasks = []
                await asyncio.sleep(1)

        # Process any remaining tasks
        if tasks:
            batch_results = await asyncio.gather(*tasks)

            for coin_result in batch_results:
                data.extend(coin_result)

        if output_format == "dataframe":
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
            df = pd.DataFrame.from_records(data, columns=columns)
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)

            return df

        return data, datetime.now(UTC).replace(microsecond=0)

    async def get_historical_ohlcv_by_start_end(self, coins, interval: str = "30m",  start_time: int = None, end_time: int = None, output_format: str = "dict"):
        interval = self._interval_map[interval]
        data = []
        tasks = []
        for symbol in coins:
            symbol = symbol.upper()
            params = {
                "symbol": symbol,
                "address": self._token_map[symbol]["address"],
                "type": interval,
                "time_from": int(start_time.timestamp()),
                "time_to": int(end_time.timestamp()),
            }
            tasks.append(self._fetch_coin_ohlcv_birdeye(params))
            # Process in batches of 15 requests per second
            if len(tasks) >= 15:
                batch_results = await asyncio.gather(*tasks)
                for coin_result in batch_results:
                    data.extend(coin_result)
                tasks = []
                await asyncio.sleep(1)

        # Process any remaining tasks
        if tasks:
            batch_results = await asyncio.gather(*tasks)

            for coin_result in batch_results:
                data.extend(coin_result)

        if output_format == "dataframe":
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
            df = pd.DataFrame.from_records(data, columns=columns)
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)

            return df

        return data, datetime.now(UTC).replace(microsecond=0)

    async def _fetch_coin_ohlcv_birdeye(
        self, params: dict
    ) -> list[dict]:
        symbol = params["symbol"]
        del params["symbol"]
        formatted_data = []

        headers = {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": self._birdeye_api_key,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._base_url}/defi/ohlcv", params=params, headers=headers
                ) as resp:
                    data = await resp.json()
        except Exception as e:
            print(f"Error fetching {symbol} {params['type']} data from Birdeye: {e}")
            return []

        if data["success"] is False or data["data"] is None:
            return []

        for entry in data["data"]["items"]:
            timestamp = entry["unixTime"]
            date_str = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d"
            )
            formatted_data.append(
                {
                    "coin": symbol,
                    "timestamp": timestamp,
                    "date": date_str,
                    "open": entry["o"],
                    "high": entry["h"],
                    "low": entry["l"],
                    "close": entry["c"],
                    "volume": entry["v"],
                }
            )

        return formatted_data


class CompositeCoinPriceDataProvider(CoinPriceDataProvider):
    def __init__(self, providers: list[CoinPriceDataProvider]):
        self.providers = providers

    async def get_current_ohlcv(self, coins, interval, output_format):
        for provider in self.providers:
            resp = await provider.get_current_ohlcv(coins, interval, output_format)
            if isinstance(resp, tuple) or len(resp) > 0:
                return resp
        return [], datetime.now(UTC).replace(microsecond=0)


    async def get_historical_ohlcv(self, coins, interval, days, output_format):
        for provider in self.providers:
            resp = await provider.get_historical_ohlcv(
                coins, interval, days, output_format
            )
            if isinstance(resp, tuple) or len(resp) > 0:
                return resp
        return [], datetime.now(UTC).replace(microsecond=0)

    async def get_historical_ohlcv_by_start_end(self, coins, interval, start_time, end_time, output_format):
        for provider in self.providers:
            resp = await provider.get_historical_ohlcv_by_start_end(
                coins, interval, start_time, end_time, output_format
            )
            if isinstance(resp, tuple) or len(resp) > 0:
                return resp
        return [], datetime.now(UTC).replace(microsecond=0)
