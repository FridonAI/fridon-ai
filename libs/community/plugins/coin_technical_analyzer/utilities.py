from typing import List, Literal, Union
from datetime import datetime, UTC, timedelta
import pyarrow.compute as pc

from fridonai_core.plugins.utilities.base import BaseUtility
from fridonai_core.plugins.utilities.llm import LLMUtility

from libs.data_providers import (
    BinanceOHLCVProvider,
    BirdeyeOHLCVProvider,
    BybitOHLCVProvider,
    CompositeCoinDataProvider,
    CoinalyzeDataProvider,
)

from libs.technical_analysis.ta import calculate_ta_indicators
from libs.technical_analysis import (
    calculate_derivative_indicators,
    generate_indicator_narrative,
)

interval_to_days = {
    "30m": 5,
    "1h": 7,
    "4h": 25,
    "1d": 100,
    "1w": 500,
}

interval_timedelta = {
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
    "1w": timedelta(weeks=1),
}


class CoinTechnicalAnalyzerUtility(LLMUtility):
    llm_job_description: str = """Assume the role of an elite crypto market analyst with deep expertise in both traditional OHLCV price signals and derivative market indicators. Your mastery in technical analysis enables you to seamlessly synthesize these datasets, providing clear and actionable insights on token performance and future price movements.

Your response should be straightforward, easily understandable, and conclude with a clear summary of the recommended market actions.

Analyze the following TA data for {symbol} coin from the most recent trading session for the specified {interval} timeframe. Considering both the price-based and derivative signals, what are the likely crypto price movements? Note: Some indicators might be unavailable due to insufficient data points.

PRICE INDICATORS (OHLCV data) for {interval} timeframe:
{coin_history_indicators}

DERIVATIVE INDICATORS for {interval} timeframe:
{derivative_indicators}
"""
    fields_to_retain: list[str] = ["plot_data"]
    model_name: str = "gpt-4o-mini"

    async def _arun(
        self,
        coin_name: str | None = None,
        coin_address: str | None = None,
        user_request: str = "",
        interval: Literal["1h", "4h", "1d", "1w"] = "4h",
        start_time: Union[str, None] = None,
        end_time: Union[str, None] = None,
        category: List[Literal["spot", "futures"]] = ["spot", "futures"],
        *args,
        **kwargs,
    ) -> dict:
        data_provider = CompositeCoinDataProvider(
            [
                BinanceOHLCVProvider(),
                BybitOHLCVProvider(),
                await BirdeyeOHLCVProvider.create(),
            ]
        )

        coinalyze_data_provider = CoinalyzeDataProvider()

        if start_time and end_time:
            start_time_dt = datetime.fromisoformat(start_time).replace(tzinfo=UTC)
            start_time_dt = start_time_dt - (interval_timedelta[interval] * 50)
            ohlcv_data = await data_provider.get_historical_ohlcv_by_start_end(
                [coin_name.upper() if coin_name else coin_address],
                interval,
                start_time_dt,
                datetime.fromisoformat(end_time).replace(tzinfo=UTC),
                output_format="dataframe",
                category=category,
            )

        else:
            ohlcv_data = await data_provider.get_historical_ohlcv(
                [coin_name.upper() if coin_name else coin_address],
                interval,
                days=interval_to_days[interval],
                output_format="dataframe",
                category=category,
            )
        if len(ohlcv_data) == 0:
            return "No data found"

        plot_data = calculate_ta_indicators(ohlcv_data, return_last_one=False)
        coin_interval_record_df = plot_data.tail(1)

        derivative_narrative = None
        if interval != "1w":
            derivative_data = coinalyze_data_provider.get_consolidated_data(
                coinalyze_data_provider._to_coinalyze_symbol_name(coin_name),
                interval=coinalyze_data_provider._to_coinalyze_interval(interval),
            )
            derivative_ta = calculate_derivative_indicators(derivative_data, ohlcv_data)
            derivative_narrative = generate_indicator_narrative(
                derivative_ta, lookback_periods=12
            )

        if len(coin_interval_record_df) == 0:
            return "No data found"
        return {
            "coin_history_indicators": str(coin_interval_record_df.to_dicts()),
            "symbol": coin_name if coin_name else coin_address,
            "plot_data": plot_data.to_dicts(),
            "interval": interval,
            "user_request": user_request,
            "derivative_indicators": derivative_narrative,
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
        coin_name: str = None,
        coin_address: str = None,
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
        category: List[Literal["spot", "futures"]] = ["spot", "futures"],
        *args,
        **kwargs,
    ) -> str:
        data_provider = CompositeCoinDataProvider(
            [
                BinanceOHLCVProvider(),
                BybitOHLCVProvider(),
                await BirdeyeOHLCVProvider.create(),
            ]
        )
        ohlcv_data = await data_provider.get_historical_ohlcv(
            [coin_name.upper() if coin_name else coin_address],
            interval,
            days=interval_to_days[interval],
            output_format="dataframe",
            category=category,
        )
        plot_data = calculate_ta_indicators(ohlcv_data, return_last_one=False)

        if len(plot_data) == 0:
            return "No coins found"

        available_indicators = [
            ind
            for ind in indicators
            if any(row[ind] is not None for row in plot_data.to_dicts())
        ]

        return {
            "plot_data": plot_data.to_dicts(),
            "indicators_to_plot": available_indicators,
        }


class CoinInfoUtility(BaseUtility):
    async def arun(
        self,
        coin_name: str | None = None,
        coin_address: str | None = None,
        interval: Literal["1h", "4h", "1d", "1w"] = "4h",
        fields: List[str] = [],
        category: List[Literal["spot", "futures"]] = ["spot", "futures"],
        **kwargs,
    ) -> str:
        response = f"Here is requested {coin_name} coin information: \n"

        if "description" in fields:
            response += "Description:\n"
            fields.remove("description")

        if len(fields) > 0:
            data_provider = CompositeCoinDataProvider(
                [
                    BinanceOHLCVProvider(),
                    BybitOHLCVProvider(),
                    await BirdeyeOHLCVProvider.create(),
                ]
            )
            ohlcv_data = await data_provider.get_historical_ohlcv(
                [coin_name.upper() if coin_name else coin_address],
                interval,
                days=interval_to_days[interval],
                output_format="dataframe",
                category=category,
            )

            if len(ohlcv_data) == 0:
                return "No data found"

            coin_latest_record = (
                calculate_ta_indicators(ohlcv_data, return_last_one=False)
                .tail(1)
                .to_dicts()
            )

            for field in fields:
                if field == "price":
                    response += f"- {field} - {coin_latest_record[0]['close']}\n"
                elif field in coin_latest_record[0]:
                    response += f"- {field} - {coin_latest_record[0][field]}\n"
            response += "In textual format."

        return response
