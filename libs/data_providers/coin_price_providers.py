import asyncio
import random
import aiohttp
import pandas as pd
from datetime import UTC, datetime, timedelta


class CoinPriceDataProvider():
    async def get_current_ohlcv(self, coins, interval, output_format): ...

    async def get_historical_ohlcv(self, coins, interval, days, output_format): ...


class DummyCoinPriceDataProvider(CoinPriceDataProvider):
    async def get_current_ohlcv(self, coins, interval='30m', output_format='dict'):
        return self._generate_coin_price_data_mock(coins)

    async def get_historical_ohlcv(self, coins, interval='30m', days=45, output_format='dict'):
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
            data.append({
                "coin": coin,
                "timestamp": timestamp,
                "date": date_str,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
            })
        return data, current_time


class BinanceCoinPriceDataProvider(CoinPriceDataProvider):
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"

    async def get_current_ohlcv(self, coins, interval='30m', output_format='dict'):
        return await self._generate_coins_price_data_binance(coins, interval, output_format=output_format)

    async def get_historical_ohlcv(self, coins, interval='30m', days=45, output_format='dict'):
        return await self._generate_historical_coins_price_data_binance(coins, interval, days, output_format=output_format)

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

    async def _fetch_coin_ohlcv_binance(self, symbol, interval, days=None, limit=1, start_time=None, end_time=None):
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

        if output_format == 'dataframe':
            columns = ['coin', 'timestamp', 'date', 'open', 'high', 'low', 'close', 'volume']
            df = pd.DataFrame.from_records(data, columns=columns)
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)

            return df

        return data, datetime.now(UTC).replace(microsecond=0)

    async def _generate_coins_price_data_binance(self, coins, interval='30m', output_format='dict'):
        return await self._generate_multiple_coins_price_data(coins, interval, output_format=output_format)

    async def _generate_historical_coins_price_data_binance(self, coins, interval='30m', days=45, output_format='dict'):
        return await self._generate_multiple_coins_price_data(coins, interval, days=days, batch_size=5, output_format=output_format)
    


class CoinPaprikaCoinPriceDataProvider(CoinPriceDataProvider):
    def __init__(self, quicknode_url: str):
        import requests
        self.base_url = f"{quicknode_url}/addon/748/v1/coins"
        response = requests.get(f"{quicknode_url}/addon/748/v1/coins")
        self.coins_symbols_to_ids = {coin["symbol"]: coin["id"] for coin in response.json()[:300]}

    async def get_current_ohlcv(self, coins, interval='30m', output_format='dict'):
        return await self._generate_coins_price_data_coinpaprika(coins, interval, output_format=output_format)

    async def get_historical_ohlcv(self, coins, interval='30m', days=45, output_format='dict'):
        return await self._generate_historical_coins_price_data_coinpaprika(coins, interval, days, output_format=output_format)

    async def _fetch_coin_ohlcv_coinpaprika(self, symbol, interval, days=None, limit=1, start_time=None, end_time=None):
        if interval == "1d":
            interval = "24h"
        if interval == "4h":
            interval = "6h"
        if days is not None:
            start_time = (datetime.now(UTC) - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
            url = f"{self.base_url}/{self.coins_symbols_to_ids[symbol]}/ohlcv/historical?&interval={interval}&start={start_time}"
            if end_time:
                url += f"&end={end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        else:   

            url = f"{self.base_url}/{self.coins_symbols_to_ids[symbol]}/ohlcv/historical?&interval={interval}&end={end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}&limit={limit}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
        except Exception as e:
            print(f"Error fetching {symbol} {interval} data from CoinPaprika: {e}")
            return []

        if days is None:
            print(f"Fetched {len(data)} {symbol} {interval} candles from CoinPaprika")

        formatted_data = []
        for entry in data:
            timestamp = int(datetime.fromisoformat(entry["time_open"]).timestamp() * 1000)
            date_str = datetime.fromtimestamp(timestamp//1000).strftime("%Y-%m-%d")
            formatted_data.append({
                "coin": symbol,
                "timestamp": timestamp,
                "date": date_str,
                "open": float(entry["open"]),
                "high": float(entry["high"]),
                "low": float(entry["low"]),
                "close": float(entry["close"]),
                "volume": float(entry["volume"]),
            })
        return formatted_data


    async def _generate_multiple_coins_price_data(self, coins, interval='30m', days=None, batch_size=5, output_format='dict'):
        data = []
        tasks = []
        now = datetime.now(UTC)
        if now.minute >= 30:
            end_time = now.replace(minute=30, second=0, microsecond=0)
        else:
            end_time = now.replace(minute=0, second=0, microsecond=0)

        print(f"Fetching latest coin prices before {end_time}")

        for symbol in coins:
            if symbol not in self.coins_symbols_to_ids:
                print(f"Coin {symbol} not found in CoinPaprika")
            tasks.append(self._fetch_coin_ohlcv_coinpaprika(symbol, interval, days=days, end_time=end_time))

        if tasks:
            result = await asyncio.gather(*tasks)
            for coin_data in result:
                data.extend(coin_data)

        if output_format == 'dataframe':
            columns = ['coin', 'timestamp', 'date', 'open', 'high', 'low', 'close', 'volume']
            df = pd.DataFrame.from_records(data, columns=columns)
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)

            return df

        return data, datetime.now(UTC).replace(microsecond=0)

    async def _generate_coins_price_data_coinpaprika(self, coins, interval='30m', output_format='dict'):
        return await self._generate_multiple_coins_price_data(coins, interval, output_format=output_format)

    async def _generate_historical_coins_price_data_coinpaprika(self, coins, interval='30m', days=45, output_format='dict'):
        return await self._generate_multiple_coins_price_data(coins, interval, days=days, batch_size=5, output_format=output_format)