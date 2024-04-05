import json
import os
from datetime import datetime, timedelta

import pandas as pd
import pandas_ta as ta
import requests


def get_chart_similar_coins(coin, start_date):
    if start_date is not None:
        start_date = datetime.fromisoformat(start_date)
        end_date = min(start_date + timedelta(days=30), datetime.now())
    else:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

    req = {
        "coin": coin,
        "from": int(start_date.timestamp()),
        "to": int(end_date.timestamp()),
        "topK": 3
    }

    print("Request", req)

    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(api_url + '/blockchain/coin-similarity', json=req).json()

    if "statusCode" in resp:
        if 500 > resp["statusCode"] >= 400:
            return resp.get("message", "Something went wrong!")
        if resp["statusCode"] >= 500:
            return "Something went wrong! Please try again later."

    print("Response", resp)
    return json.dumps({
        "type": "similar_coins",
        "coin": coin,
        "start_date_timestamp": int(start_date.timestamp()),
        "end_date_timestamp": int(end_date.timestamp()),
        "start_date": start_date.strftime("%d %B %Y"),
        "end_date": end_date.strftime("%d %B %Y"),
        **resp,
    })


def _read_ohlcv_date(symbol: str) -> pd.DataFrame:
    time_to = int(datetime.now().timestamp())
    time_from = int((time_to - timedelta(days=120).total_seconds()))
    resp = requests.get(f'https://api.kraken.com/0/public/OHLC?pair={symbol.upper()}USD&interval=1440&since={time_from}')
    data = resp.json()['result'][f'{symbol.upper()}USD']
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


def get_coin_ta(coin):
    df = _read_ohlcv_date(coin)
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
