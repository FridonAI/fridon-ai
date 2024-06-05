import json
import os
from datetime import datetime, timedelta

import pandas as pd
import requests

from app.core.plugins.utilities import BaseUtility


class CoinTechnicalAnalyzerUtility(BaseUtility):
    name = "coin-technical-analyzer"
    description = "A utility that allows you to analyze coin by technical indicators"

    def _read_ohlcv_date(self, symbol: str) -> pd.DataFrame:
        time_to = int(datetime.now().timestamp())
        time_from = int((time_to - timedelta(days=120).total_seconds()))
        resp = requests.get(
            f'https://api.kraken.com/0/public/OHLC?pair={symbol.upper()}USD&interval=1440&since={time_from}')

        response_data = resp.json()

        if resp.status_code != 200 or len(response_data['error']) > 0:
            raise Exception(f"Failed to fetch data from Kraken API. Status code: {resp.status_code}")

        data = list(response_data['result'].values())[0]
        df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
        df.drop(columns=['vwap', 'count'], inplace=True)
        df.rename(columns={'time': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df.set_index('date', inplace=True)
        df = df.iloc[:-1]
        return df

    async def run(
            self,
            coin_name: str,
            *args,
            **kwargs
    ) -> str:
        df = self._read_ohlcv_date(coin_name)
        df.ta.macd(append=True)
        df.ta.rsi(append=True)
        df.ta.bbands(append=True)
        df.ta.obv(append=True)

        df.ta.sma(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.stoch(append=True)
        df.ta.adx(append=True)

        df.ta.willr(append=True)
        df.ta.cmf(append=True)
        df.ta.psar(append=True)

        df['OBV_in_million'] = df['OBV'] / 1e7
        df['MACD_histogram_12_26_9'] = df['MACDh_12_26_9']

        last_day_summary = df.iloc[-1][['close',
                                        'MACD_12_26_9', 'MACD_histogram_12_26_9', 'RSI_14', 'BBL_5_2.0', 'BBM_5_2.0',
                                        'BBU_5_2.0', 'SMA_20', 'EMA_50', 'OBV_in_million', 'STOCHk_14_3_3',
                                        'STOCHd_14_3_3', 'ADX_14', 'WILLR_14', 'CMF_20',
                                        'PSARl_0.02_0.2', 'PSARs_0.02_0.2'
                                        ]]

        return str(last_day_summary)
