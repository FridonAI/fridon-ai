from typing import List, Literal, Union
from datetime import datetime, UTC
import pyarrow.compute as pc

from fridonai_core.plugins.utilities.base import BaseUtility
from fridonai_core.plugins.utilities.llm import LLMUtility
from libs.repositories import IndicatorsRepository


class CoinTechnicalAnalyzerUtility(LLMUtility):
    llm_job_description: str = """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
Your mastery encompasses both stock fundamentals and intricate technical indicators. \
You possess the ability to decode complex market dynamics, \
providing clear insights and recommendations backed by a thorough understanding of interrelated factors. \
Your expertise extends to practical tools like the pandas_ta module, \
allowing you to navigate data intricacies with ease. \
As a TA authority, your role is to decipher market trends, make informed predictions, and offer valuable perspectives.

Generated response should be simple, easy to understand, user shouldn't try hard to understand what's happening, conclusion should be main part of the analysis.

Given {symbol} coin's TA data as below on the last trading day, what will be the next few days possible crypto price movement?

Technical Indicators for {interval} intervals:
{coin_history_indicators}"""
    fields_to_retain: list[str] = ["plot_data"]

    async def _arun(
        self,
        coin_name: str,
        interval: Literal["1h", "4h", "1d", "1w"] = "4h",
        start_time: Union[str, None] = None,
        end_time: Union[str, None] = None,
        *args,
        **kwargs,
    ) -> dict:
        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )
        if start_time and end_time:
            coin_interval_record_df = (
                indicators_repository.get_coin_records_in_time_range(
                    coin_name.upper(),
                    datetime.fromisoformat(start_time).replace(tzinfo=UTC),
                    datetime.fromisoformat(end_time).replace(tzinfo=UTC),
                )
            )
            plot_data = coin_interval_record_df.to_dicts()

        else:
            coin_interval_record_df = indicators_repository.get_coin_latest_record(
                coin_name.upper()
            )
            plot_data = indicators_repository.get_coin_last_records(
                coin_name.upper(), number_of_points=200
            ).to_dicts()

        if len(coin_interval_record_df) == 0:
            return "No data found"

        return {
            "coin_history_indicators": str(coin_interval_record_df.to_dicts()),
            "symbol": coin_name,
            "plot_data": plot_data,
            "interval": interval,
        }


class CoinTechnicalIndicatorsListUtility(BaseUtility):
    async def arun(self, indicator_name: str = None, *args, **kwargs) -> str:

        indicators = {
            'MACD_12_26_9': 'Moving Average Convergence Divergence (MACD). Uses 12-day and 26-day Exponential Moving Averages (EMAs) to signal trend direction and strength. A bullish signal occurs when the MACD line crosses above the signal line (9-day EMA), and a bearish signal occurs when the MACD line crosses below the signal line.',
            'MACD_histogram_12_26_9': 'MACD Histogram. Represents the difference between the MACD line and the signal line. Positive values suggest bullish momentum, while negative values indicate bearish momentum. Changes in the histogram’s direction can hint at an impending trend reversal.',
            'RSI_14': 'Relative Strength Index (14-day). Measures the speed and change of price movements, indicating overbought or oversold conditions. A value above 70 suggests an overbought condition (potential for a price decline), and a value below 30 suggests oversold (potential for a price increase).',
            'BBL_5_2.0': 'Bollinger Bands Lower Band (5-period, 2 standard deviations). The lower boundary of price volatility. Prices near the lower band may indicate oversold conditions, signaling potential buying opportunities.',
            'BBM_5_2.0': 'Bollinger Bands Middle Band (5-period). Represents the simple moving average (SMA) of the price. It serves as the basis for the upper and lower bands and helps identify price trends.',
            'BBU_5_2.0': 'Bollinger Bands Upper Band (5-period, 2 standard deviations). The upper boundary of price volatility. Prices near the upper band may indicate overbought conditions, signaling potential selling opportunities.',
            'SMA_20': 'Simple Moving Average (20-period). Calculates the average price over the last 20 periods. Price movements above the SMA suggest bullish trends, while prices below it suggest bearish trends.',
            'EMA_50': 'Exponential Moving Average (50-period). Similar to the SMA but gives more weight to recent prices, allowing it to react more quickly to price changes. Useful for identifying trends and potential support/resistance levels.',
            'OBV_in_million': 'On-Balance Volume (OBV, in millions). Relates volume to price movements. A rising OBV suggests buying pressure (potential bullishness), while a falling OBV suggests selling pressure (potential bearishness).',
            'STOCHk_14_3_3': 'Stochastic Oscillator %K (14, 3, 3). Measures the current closing price relative to the high-low range over 14 periods. Values above 80 indicate overbought conditions, while values below 20 indicate oversold conditions. Often used in conjunction with %D for buy/sell signals.',
            'STOCHd_14_3_3': 'Stochastic Oscillator %D (14, 3, 3). A 3-period simple moving average of %K, smoothing out the %K line. It is used alongside %K to generate more reliable buy/sell signals.',
            'ADX_14': 'Average Directional Index (14-day). Measures the strength of a trend. A value above 25 indicates a strong trend (either up or down), while values below 20 suggest a weak or sideways market. Does not indicate trend direction on its own.',
            'WILLR_14': 'Williams %R (14-day). Momentum indicator that measures overbought and oversold levels, with values ranging from 0 to -100. A reading above -20 indicates overbought conditions, while a reading below -80 indicates oversold conditions. Similar to the Stochastic Oscillator.',
            'CMF_20': 'Chaikin Money Flow (20-day). Measures the accumulation or distribution of a security by comparing the closing price to the high-low range. Positive values suggest buying pressure, while negative values suggest selling pressure.',
            'PSARl_0.02_0.2': 'Parabolic SAR (long-term, 0.02 step, 0.2 max). Identifies potential trend reversals. When dots appear below the price, it signals a bullish trend; when they appear above, it signals a bearish trend. This setting is typically used for long-term analysis.',
            'PSARs_0.02_0.2': 'Parabolic SAR (short-term, 0.02 step, 0.2 max). Similar to the long-term PSAR but designed for shorter-term price movements, making it more sensitive to short-term trend reversals.'
        }

        if indicator_name and indicator_name in indicators:
            return f'Description of indicator: {indicator_name}: {indicators[indicator_name]}'

        return "\n".join([
            f"{name}:\n\t{description}"
            for name, description in indicators.items()
        ])


class CoinChartPlotterUtility(BaseUtility):
    async def arun(
        self,
        coin_name: str,
        indicators: List[str] = [
            "MACD_12_26_9",
            "MACD_histogram_12_26_9",
            "RSI_14",
            "BBL_5_2.0",
            "BBM_5_2.0",
            "BBU_5_2.0",
            "SMA_20",
            "EMA_50",
            "OBV_in_million",
            "STOCHk_14_3_3",
            "STOCHd_14_3_3",
            "ADX_14",
            "WILLR_14",
            "CMF_20",
            "PSARl_0.02_0.2",
            "PSARs_0.02_0.2",
        ],
        interval: Literal["1h", "4h", "1d", "1w"] = "4h",
        *args,
        **kwargs,
    ) -> str:
        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval}"
        )
        print("Want these indicators", indicators)
        coin_last_records = indicators_repository.get_coin_last_records(
            coin_name, number_of_points=200
        )

        if len(coin_last_records) == 0:
            return "No coins found"

        return {
            "plot_data": coin_last_records.to_dicts(),
            "indicators_to_plot": indicators,
        }


class CoinInfoUtility(BaseUtility):
    async def arun(
        self, coin_name: str, *args, fields: List[str] = [], **kwargs
    ) -> str:
        response = "Here are coin info you requested: \n"

        if "description" in fields:
            response += "Description:\n"
            fields.remove("description")

        if len(fields) > 0:
            indicators_repository = IndicatorsRepository(table_name="indicators_raw")
            coin_latest_record = indicators_repository.get_coin_latest_record(
                coin_name
            ).to_dicts()
            print("Coin latest record: ", coin_latest_record)
            if len(coin_latest_record) == 0:
                return "No data found"

            for field in fields:
                if field == "price":
                    response += f"- {field}: {coin_latest_record[0]['close']}\n"
                elif field in coin_latest_record[0]:
                    response += f"- {field}: {coin_latest_record[0][field]}\n"

        return response
