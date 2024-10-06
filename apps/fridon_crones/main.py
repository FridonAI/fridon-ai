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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COINS = ["BTC"]


def generate_dummy_data():
    data = []
    current_time = datetime.datetime.utcnow().replace(microsecond=0)
    timestamp = int(current_time.timestamp() * 1000)
    date_str = current_time.strftime("%Y-%m-%d")
    for coin in COINS:
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


@aiocron.crontab("*/1 * * * *", start=True)
async def data_ingestion_job():
    logger.info("\n\nStarting data ingestion job.")
    await update_ohlcv_data()
    await update_indicators_data()


async def update_ohlcv_data():
    raw_data, current_time = generate_dummy_data()
    raw_repository = OhlcvRepository(table_name="ohlcv_raw")
    df = pl.from_records(raw_data)

    raw_repository.write(df)

    # intervals = [
    #     ('1h', datetime.timedelta(hours=1)),
    #     ('4h', datetime.timedelta(hours=4)),
    #     ('1d', datetime.timedelta(days=1)),
    #     ('1w', datetime.timedelta(weeks=1)),
    # ]
    intervals = [
        ("1h", datetime.timedelta(minutes=2)),
        ("4h", datetime.timedelta(minutes=4)),
        # ('1d', datetime.timedelta(minutes=5)),
        # ('1w', datetime.timedelta(minutes=20)),
    ]
    for interval_name, interval_length in intervals:
        interval_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
        await update_interval_data(
            interval_repository, interval_name, interval_length, df, current_time
        )


async def update_interval_data(
    repository, interval_name, interval_length, new_data_df, current_time
):
    logger.info(f"Updating interval data for {interval_name}.")
    coin = COINS[0]
    interval_start_time = current_time - (
        datetime.timedelta(seconds=interval_length.total_seconds() - 1)
    )

    filters = (
        pc.field("timestamp") >= pc.scalar(int(interval_start_time.timestamp() * 1000))
    ) & (pc.field("coin") == pc.scalar(coin))

    try:
        existing_df = repository.read(filters=filters)
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
    # interval_end_time = interval_start_time + {
    #     '1h': datetime.timedelta(hours=1),
    #     '4h': datetime.timedelta(hours=4),
    #     '1d': datetime.timedelta(days=1),
    #     '1w': datetime.timedelta(weeks=1),
    # }[interval_name]

    interval_end_time = (
        interval_start_time
        + {
            "1h": datetime.timedelta(minutes=2),
            "4h": datetime.timedelta(minutes=4),
            # '1d': datetime.timedelta(minutes=5),
            # '1w': datetime.timedelta(minutes=20),
        }[interval_name]
    )

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
    tokens = ["BTC"]

    interval_names = ["raw", "1h", "4h"]

    for interval_name in interval_names:
        try:
            ohlcv_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
            indicators_repository = IndicatorsRepository(
                table_name=f"indicators_{interval_name}"
            )

            df = ohlcv_repository.read(
                filters=pc.field("coin").isin(tokens),
                columns=["coin", "timestamp", "open", "high", "low", "close", "volume"],
                last_n=50,
                order_by="timestamp",
            )

            logger.info(f"Calculating indicators for {interval_name}.")
            df_indicators = calculate_ta_indicators(df)
            df_bulish = await calculate_bulish_indicator(df_indicators)
            df_indicators_merged = df_indicators.join(
                df_bulish, on=["coin", "timestamp"], how="left"
            )
            indicators_repository.update(
                df_indicators_merged, predicate="s.timestamp == t.timestamp"
            )
            logger.info(f"Updated indicators data for {interval_name}.")
        except Exception as e:
            logger.error(f"Error updating indicators data for {interval_name}: {e}")


def main():
    logger.info("Starting the scheduler.")
    logger.info(f"Start time: {datetime.datetime.now().isoformat()}")
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
