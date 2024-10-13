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

    async def _fetch_coin_ohlcv_binance(self, symbol, interval, days=None, limit=2, start_time=None, end_time=None):
        if days is not None:
            start_time = int((datetime.now(UTC) - timedelta(days=days)).timestamp() * 1000)
            url = f"{self.base_url}?symbol={symbol}USDT&interval={interval}&startTime={start_time}"
        else:
            url = f"{self.base_url}?symbol={symbol}USDT&interval={interval}&limit={limit}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        if days is None:
            data = [entry for entry in data if int(entry[0]) <= end_time]
            if data:
                data = [max(data, key=lambda x: int(x[0]))]
            else:
                raise ValueError(f"No current data found for {symbol}")
            

        formatted_data = []
        for entry in data:
            timestamp = int(entry[0])
            date_str = datetime.fromtimestamp(timestamp//1000).strftime("%Y-%m-%d")
            formatted_data.append({
                "coin": symbol,
                "timestamp": timestamp,
                "date": date_str,
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5]),
            })
        return formatted_data


    async def _generate_multiple_coins_price_data(self, coins, interval='30m', days=None, batch_size=5, output_format='dict'):
        data = []
        tasks = []
        end_time = int((datetime.now(UTC) - timedelta(seconds=50)).timestamp() * 1000)

        if days is None:
            print(f"Fetching latest coin prices before {end_time}")

        for i, symbol in enumerate(coins):
            tasks.append(self._fetch_coin_ohlcv_binance(symbol, interval, days=days, end_time=end_time))
            if (i + 1) % batch_size == 0:
                result = await asyncio.gather(*tasks)
                for coin_data in result:
                    data.extend(coin_data)
                tasks = []
                await asyncio.sleep(1)

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
        return await self._generate_multiple_coins_price_data(coins, interval, days=days, batch_size=8, output_format=output_format)