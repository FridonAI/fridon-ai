import asyncio
import datetime
import logging
import os

import aiocron
import polars as pl
import pyarrow.compute as pc

from libs.internals.indicators import calculate_ta_indicators
from libs.repositories import IndicatorsRepository, OhlcvRepository

if os.environ.get("DATA_PROVIDER") == "binance":
    from libs.data_providers import BinanceCoinPriceDataProvider as DataProvider
elif os.environ.get("DATA_PROVIDER") == "coinpaprika":
    from libs.data_providers import CoinPaprikaCoinPriceDataProvider as DataProvider
else:
    from libs.data_providers import DummyCoinPriceDataProvider as DataProvider


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

interval_names = ["raw", "1h", "4h", "1d"] #, "1w"]

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
    "DOGE",
    "TAO",
    "FET",
    "SANTOS",
    "WLD",
    "SHIB",
    "APT",
    "FTM",
    "EIGEN",
    "PEOPLE",
    "SAGA",
    "RUNE",
    "NEAR",
    "1000SATS",
    "BONK",
    "FLOKI",
    "NOT",
    "DOGS",
    "1MBABYDOGE",
    "CFX",
    "TURBO",
    "AVAX",
    "BOME",
    "WING",
    "LAZIO",
    "CVC",
    "ENA",
    "TRX",
    "ORDI",
    "ARB",
    "HMSTR",
    "LINK",
    "EUR",
    "CATI",
    "BNX",
    "RENDER",
    "TON",
    "TIA",
    "ADA",
    "AAVE",
    "ALPINE",
    "INJ",
    "ZRO",
    "ZK",
    "USTC",
    "MKR",
    "LTC",
    "PORTO",
    "DIA",
    "ARKM",
    # "MATIC",
    "PENDLE",
    "ICP",
    "ALT",
    "IO",
    "FIL",
    "GALA",
    "OP",
    "JUP",
    "BCH",
    "STX",
    "ASR",
    "UNI",
    "CELO",
    "BANANA",
    "W",
    "POL",
    "TROY",
    "LUNC",
    "ATM",
    "MANTA",
    "DYDX",
    "CRV",
    "STRK",
    "DOT",
    "FORTH",
    "LUNA",
    "ACH",
    "CHZ",
    "ATOM",
    "YGG",
    "PHB",
    "AR",
    "JTO",
    "LDO",
    "HBAR",
    "SUPER",
    "FIDA",
    "MEME",
    "CKB",
    "OMNI",
    "PYTH",
    "PSG",
    "DEGO",
    "OM",
    "BEAMX",
    "BB",
    "EURI",
    "JASMY",
    "RAY",
    "SUN",
    "PIXEL",
    "BLUR",
    "ROSE",
    "GRT",
    "TRB",
    # "VGX",
    "WOO",
    "IMX",
    "SSV",
    "AI",
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


# @aiocron.crontab("0,30 * * * *", start=True)
async def data_ingestion_job():
    logger.info(f"\n\nStarting data ingestion job. {datetime.datetime.now(datetime.UTC).isoformat()}\n\n")
    await update_ohlcv_data()
    await update_indicators_data()


async def update_ohlcv_data():
    data_provider = DataProvider()
    raw_data, _ = await data_provider.get_current_ohlcv(COINS, interval="30m")
    current_time = datetime.datetime.fromtimestamp(raw_data[0]["timestamp"] // 1000)
    raw_repository = OhlcvRepository(table_name="ohlcv_raw")
    df = pl.from_records(raw_data)

    raw_repository.update(df, predicate="s.timestamp == t.timestamp")

    for interval_name in interval_names[1:]:
        interval_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
        await update_interval_data(
            interval_repository,
            interval_name,
            df,
            current_time,
        )


async def update_interval_data(
    repository: OhlcvRepository, 
    interval_name: str, 
    new_data_df: pl.DataFrame, 
    current_time: datetime.datetime
):
    logger.info(f"Updating interval data for {interval_name}.")
    try:
        existing_df = repository.get_last_records(number_of_points=1, last_n=True)
        logger.info(f"Existing records for {interval_name}: {existing_df.shape[0]}")
    except Exception as e:
        logger.error(f"Error reading interval data for {interval_name}: {e}")
        existing_df = pl.DataFrame()

    if not existing_df.is_empty():
        logger.info(f"Updating existing interval record for {interval_name}.")
        updated_df = update_interval_record(existing_df, new_data_df)

        repository.update(updated_df, predicate="s.timestamp == t.timestamp AND s.coin == t.coin")
    else:
        logger.info(f"Creating new interval record for {interval_name}.")
        new_interval_df = create_new_interval_record(
            current_time, interval_name, new_data_df
        )
        repository.update(new_interval_df, predicate="s.timestamp == t.timestamp AND s.coin == t.coin")


def update_interval_record(existing_df, new_data_df):
    updated_df = existing_df.join(new_data_df, on=["coin"], how="left", suffix="_new")
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
    interval_start_time: datetime.datetime, 
    interval_name: str, 
    new_data_df: pl.DataFrame
):
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
    for interval_name in interval_names:
        logger.info(f"Calculating indicators for {interval_name}.")
        ohlcv_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
        indicators_repository = IndicatorsRepository(table_name=f"indicators_{interval_name}")
        update_indicators_df = pl.DataFrame()

        last_coins_records_df = ohlcv_repository.get_last_records(
            number_of_points=50, 
            columns=[
                "coin",
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ],
            last_n=True,                 
        )
        logger.info(f"Fetched Last coins records for {interval_name}: {last_coins_records_df.shape[0]}, total coins: {len(COINS)}")
        for coin in COINS:
            last_coin_records_df = last_coins_records_df.filter(pl.col("coin") == coin)
            try:
                last_coin_records_indicators_df = calculate_ta_indicators(last_coin_records_df)
            except Exception as e:
                logger.error(f"Error calculating indicators for {coin}-{interval_name}: {e}")
                continue

            if update_indicators_df.is_empty():
                update_indicators_df = last_coin_records_indicators_df
            else:
                update_indicators_df = pl.concat([update_indicators_df, last_coin_records_indicators_df], how="vertical_relaxed")

        if not update_indicators_df.is_empty():
            indicators_repository.update(update_indicators_df, predicate="s.timestamp == t.timestamp AND s.coin == t.coin")
            logger.info(f"Write indicators data for {interval_name}.")



async def seed():
    logger.info("Start Seeding Prices and Indicators data.")
    interval_to_days = {
        "30m": 3,
        "1h": 5,
        "4h": 22,
        "1d": 80,
        "1w": 400,
    }

    data_provider = DataProvider()
    for interval_name in interval_names:
        start_time = datetime.datetime.now()
        logger.info(f"**************************************************")
        logger.info(f"Seeding ohlcv data with indicators for {interval_name}.")
        ohlcv_repository = OhlcvRepository(table_name=f"ohlcv_{interval_name}")
        indicators_repository = IndicatorsRepository(
            table_name=f"indicators_{interval_name}"
        )
        if interval_name == "raw":
            interval_name = "30m"

        
        
        
        for i in range(0, len(COINS), 20):
            coin_chunk = COINS[i:i+20]
            logger.info(f"Handling coins {coin_chunk}")
            raw_data, _ = await data_provider.get_historical_ohlcv(
                coin_chunk, interval=interval_name, days=interval_to_days[interval_name]
            )
            df = pl.from_records(raw_data)
            logger.info(f"Records fetched: {df.shape[0]}")
            ohlcv_repository.write(df)

            seed_indicators_df = pl.DataFrame()
            
            for coin in coin_chunk:
                coin_df = df.filter(pl.col("coin") == coin).select([
                    "coin", "timestamp", "open", "high", "low", "close", "volume"
                ])
                try:
                    df_indicators = calculate_ta_indicators(coin_df, return_last_one=False)
                except Exception as e:
                    logger.error(f"Error calculating indicators for {coin}: {e}")
                    continue
                if seed_indicators_df.is_empty():
                    seed_indicators_df = df_indicators
                else:
                    seed_indicators_df = pl.concat([seed_indicators_df, df_indicators], how="vertical_relaxed")
                    
                if seed_indicators_df.shape[0] > 4000:
                    logger.info(f"Number of records to update: {seed_indicators_df.shape[0]}")
                    indicators_repository.write(seed_indicators_df)
                    seed_indicators_df = pl.DataFrame()

            if not seed_indicators_df.is_empty():
                indicators_repository.write(seed_indicators_df)
            else:
                logger.warning("No indicators data to update.")

        elapsed_time = datetime.datetime.now() - start_time
        logger.info(f"Seeded indicators data for {interval_name} Finished. Time taken: {elapsed_time}")

    logger.info("****************** Seeding Prices and Indicators data Finished. ******************")


async def process(loop):
    await seed()
    # await data_ingestion_job()
    aiocron.crontab("0,30 * * * *", data_ingestion_job, loop=loop)

def main():
    logger.info("Starting the scheduler.")
    logger.info(f"Start time: {datetime.datetime.now(datetime.UTC).isoformat()}")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(process(loop))
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
