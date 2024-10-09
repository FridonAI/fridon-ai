import asyncio
import datetime
import logging
import os
import random

import aiocron
import pandas as pd
import pandas_ta as ta
import polars as pl
import pyarrow as pa
import pyarrow.compute as pc

from libs.internals.indicators import (
    calculate_bulish_indicator,
    calculate_ta_indicators,
)
from libs.repositories import IndicatorsRepository, OhlcvRepository

if os.environ.get("DATA_PROVIDER") == "binance":
    from libs.data_providers import BinanceCoinPriceDataProvider as DataProvider
else:
    from libs.data_providers import DummyCoinPriceDataProvider as DataProvider


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COINS = [
    "BTC",
    "ETH",
    "NEIRO",
    "SOL",
    "SUI",
    "PEPE",
    "OG",
    "WIF",
    "FTT",
    "BNB",
    "XRP",
    "SEI",
    # "DOGE",
    # "TAO",
    # "FET",
    # "SANTOS",
    # "WLD",
    # "SHIB",
    # "APT",
    # "FTM",
    # "EIGEN",
    # "PEOPLE",
    # "SAGA",
    # "RUNE",
    # "NEAR",
    # "1000SATS",
    # "BONK",
    # "FLOKI",
    # "NOT",
    # "DOGS",
    # "1MBABYDOGE",
    # "CFX",
    # "TURBO",
    # "AVAX",
    # "BOME",
    # "WING",
    # "LAZIO",
    # "CVC",
    # "ENA",
    # "TRX",
    # "ORDI",
    # "ARB",
    # "HMSTR",
    # "LINK",
    # "EUR",
    # "CATI",
    # "BNX",
    # "RENDER",
    # "TON",
    # "TIA",
    # "ADA",
    # "AAVE",
    # "ALPINE",
    # "INJ",
    # "ZRO",
    # "ZK",
    # "USTC",
    # "MKR",
    # "LTC",
    # "PORTO",
    # "DIA",
    # "ARKM",
    # "MATIC",
    # "PENDLE",
    # "ICP",
    # "ALT",
    # "IO",
    # "FIL",
    # "GALA",
    # "OP",
    # "JUP",
    # "BCH",
    # "STX",
    # "ASR",
    # "UNI",
    # "CELO",
    # "BANANA",
    # "W",
    # "POL",
    # "TROY",
    # "LUNC",
    # "ATM",
    # "MANTA",
    # "DYDX",
    # "CRV",
    # "STRK",
    # "DOT",
    # "FORTH",
    # "LUNA",
    # "ACH",
    # "CHZ",
    # "ATOM",
    # "YGG",
    # "PHB",
    # "AR",
    # "JTO",
    # "LDO",
    # "HBAR",
    # "SUPER",
    # "FIDA",
    # "MEME",
    # "CKB",
    # "OMNI",
    # "PYTH",
    # "PSG",
    # "DEGO",
    # "OM",
    # "BEAMX",
    # "BB",
    # "EURI",
    # "JASMY",
    # "RAY",
    # "SUN",
    # "PIXEL",
    # "BLUR",
    # "ROSE",
    # "GRT",
    # "TRB",
    # "VGX",
    # "WOO",
    # "IMX",
    # "SSV",
    # "AI",
    # "BAR",
    # "GAS",
    # "KAVA",
    # "DYM",
    # "JUV",
    # "ETC",
    # "CITY",
    # "XAI",
    # "ASTR",
    # "CVP",
    # "VIDT",
    # "ACM",
    # "MASK",
    # "ENS",
    # "RSR",
    # "ARK",
    # "APE",
    # "AUDIO",
    # "PORTAL",
    # "REI",
    # "CAKE",
    # "REZ",
    # "MINA",
    # "VET",
    # "ORN",
    # "ALGO",
    # "VANRY",
    # "AST",
    # "HIGH",
    # "GMT",
    # "AEVO",
    # "LEVER",
    # "FIO",
    # "EOS",
    # "AXS",
    # "SNT",
    # "AXL",
    # "UNFI",
    # "COS",
    # "REEF",
    # "XLM",
    # "TRU",
    # "AMP",
    # "TNSR",
    # "EPX",
    # "COTI",
    # "THETA",
    # "VIC",
    # "RAD",
    # "CYBER",
    # "RARE",
    # "EDU",
    # "EGLD",
    # "UMA",
    # "LISTA",
    # "LPT",
    # "FOR",
    # "ACE",
    # "NEO",
    # "BAKE",
    # "SYN",
    # "FRONT",
    # "SNX",
    # "KDA",
    # "TWT",
    # "DODO",
    # "ONG",
    # "CTXC",
    # "FLOW",
    # "RDNT",
    # "VIB",
    # "SLF",
    # "PYR",
]


@aiocron.crontab("*/1 * * * *", start=True)
async def data_ingestion_job():
    logger.info("\n\nStarting data ingestion job.")
    await update_ohlcv_data()
    await update_indicators_data()


async def update_ohlcv_data():
    data_provider = DataProvider()
    raw_data, _ = await data_provider.get_current_ohlcv(COINS, interval="30m")
    current_time = datetime.datetime.fromtimestamp(raw_data[0]["timestamp"] // 1000)
    raw_repository = OhlcvRepository(table_name="ohlcv_raw")
    df = pl.from_records(raw_data)

    raw_repository.write(df)

    intervals = [
        ("1h", datetime.timedelta(hours=1)),
        ("4h", datetime.timedelta(hours=4)),
        ("1d", datetime.timedelta(days=1)),
        ("1w", datetime.timedelta(weeks=1)),
    ]
    # intervals = [
    #     ("1h", datetime.timedelta(minutes=2)),
    #     ("4h", datetime.timedelta(minutes=4)),
    #     # ('1d', datetime.timedelta(minutes=5)),
    #     # ('1w', datetime.timedelta(minutes=20)),
    # ]
    for interval_name, interval_length in intervals:
        interval_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
        await update_interval_data(
            interval_repository,
            interval_name,
            interval_length,
            df,
            current_time,
        )


async def update_interval_data(
    repository, interval_name, interval_length, new_data_df, current_time
):
    logger.info(f"Updating interval data for {interval_name}.")
    interval_start_time = current_time - (
        datetime.timedelta(seconds=interval_length.total_seconds() - 1)
    )

    filters = (
        pc.field("timestamp") >= pc.scalar(int(interval_start_time.timestamp() * 1000))
    ) & (pc.field("coin").isin(COINS))

    try:
        existing_df = repository.read(filters=filters)
        print(existing_df.shape[0])
    except Exception as e:
        logger.error(f"Error reading interval data for {interval_name}: {e}")
        existing_df = pl.DataFrame()

    if not existing_df.is_empty():
        logger.info(f"Updating existing interval record for {interval_name}.")
        updated_df = update_interval_record(existing_df, new_data_df)

        repository.update(updated_df, predicate="s.timestamp == t.timestamp")
    else:
        logger.info(f"Creating new interval record for {interval_name}.")
        new_interval_df = create_new_interval_record(
            current_time, interval_name, new_data_df
        )
        print("New interval record", new_interval_df)
        repository.write(new_interval_df)


def update_interval_record(existing_df, new_data_df):
    new_data_pl = new_data_df
    updated_df = existing_df.join(new_data_pl, on=["coin"], how="left", suffix="_new")
    updated_df = updated_df.with_columns(
        [
            pl.when(pl.col("high_new") > pl.col("high"))
            .then(pl.col("high_new"))
            .otherwise(pl.col("high"))
            .alias("high"),
            pl.when(pl.col("low_new") < pl.col("low"))
            .then(pl.col("low_new"))
            .otherwise(pl.col("low"))
            .alias("low"),
            pl.col("close_new").alias("close"),
            (pl.col("volume") + pl.col("volume_new")).alias("volume"),
        ]
    )

    updated_df = updated_df.drop(
        [
            "open_new",
            "high_new",
            "low_new",
            "close_new",
            "volume_new",
            "timestamp_new",
            "date_new",
        ]
    )
    return updated_df


def create_new_interval_record(
    interval_start_time, interval_name, new_data_df: pl.DataFrame
):
    interval_end_time = (
        interval_start_time
        + {
            "1h": datetime.timedelta(hours=1),
            "4h": datetime.timedelta(hours=4),
            "1d": datetime.timedelta(days=1),
            "1w": datetime.timedelta(weeks=1),
        }[interval_name]
    )

    # interval_end_time = (
    #     interval_start_time
    #     + {
    #         "1h": datetime.timedelta(minutes=2),
    #         "4h": datetime.timedelta(minutes=4),
    #         # '1d': datetime.timedelta(minutes=5),
    #         # '1w': datetime.timedelta(minutes=20),
    #     }[interval_name]
    # )

    df = new_data_df

    if df.shape[0] == 0:
        logger.warning(f"No data to create new interval record for {interval_name}.")
        return pl.DataFrame()

    aggregated_df = df.group_by("coin").agg(
        [
            pl.first("open").alias("open"),
            pl.max("high").alias("high"),
            pl.min("low").alias("low"),
            pl.last("close").alias("close"),
            pl.sum("volume").alias("volume"),
        ]
    )

    aggregated_df = aggregated_df.with_columns(
        [
            pl.lit(int(interval_start_time.timestamp() * 1000)).alias("timestamp"),
            pl.lit(interval_start_time.strftime("%Y-%m-%d")).alias("date"),
        ]
    )

    return aggregated_df


async def update_indicators_data():
    interval_names = ["raw", "1h", "4h"]

    for interval_name in interval_names:
        try:
            ohlcv_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
            indicators_repository = IndicatorsRepository(
                table_name=f"indicators_{interval_name}"
            )

            delta = {
                "raw": datetime.timedelta(minutes=30 * 50),
                "1h": datetime.timedelta(hours=1 * 50),
                "4h": datetime.timedelta(hours=4 * 50),
                "1d": datetime.timedelta(days=1 * 50),
                "1w": datetime.timedelta(days=7 * 50),
            }[interval_name]

            for coin in COINS:
                df = ohlcv_repository.read(
                    filters=(pc.field("coin") == pc.scalar(coin))
                    & (
                        pc.field("timestamp")
                        >= int((datetime.datetime.utcnow() - delta).timestamp() * 1000)
                    )
                    & (
                        pc.field("timestamp")
                        <= int(datetime.datetime.utcnow().timestamp() * 1000)
                    ),
                    columns=[
                        "coin",
                        "timestamp",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                    ],
                )

            logger.info(f"Calculating indicators for {interval_name}.")
            df_indicators = calculate_ta_indicators(df)
            # df_bulish = await calculate_bulish_indicator(df_indicators)
            # df_indicators_merged = df_indicators.join(
            #     df_bulish, on=["coin", "timestamp"], how="left"
            # )
            indicators_repository.update(
                df_indicators, predicate="s.timestamp == t.timestamp"
            )
            logger.info(f"Updated indicators data for {interval_name}.")
        except Exception as e:
            logger.error(f"Error updating indicators data for {interval_name}: {e}")


async def seed():
    for interval_name in ["raw", "1h", "4h", "1d", "1w"]:
        ohlcv_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
        if interval_name == "raw":
            interval_name = "30m"
        data_provider = DataProvider()
        raw_data, _ = await data_provider.get_historical_ohlcv(
            COINS, interval=interval_name, days=7
        )
        df = pl.from_records(raw_data)
        ohlcv_repository.write(df)


def main():
    logger.info("Starting the scheduler.")
    logger.info(f"Start time: {datetime.datetime.now().isoformat()}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(seed())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
