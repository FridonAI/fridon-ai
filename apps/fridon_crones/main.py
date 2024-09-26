import asyncio
import aiocron 
import polars as pl
import pyarrow as pa
import logging
import os
import datetime
import pandas as pd 
import random
from libs.repositories import coins_delta_lake_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COINS = ['BTC']

def initialize_tables():
    ohlcv_schema = pa.schema([
        ('coin', pa.string()),
        ('timestamp', pa.int64()),
        ('date', pa.string()),
        ('open', pa.float64()),
        ('high', pa.float64()),
        ('low', pa.float64()),
        ('close', pa.float64()),
        ('volume', pa.float64()),
    ])
    partition_columns = ['date', 'timestamp']

    coins_delta_lake_repository.initialize_table('ohlcv_raw', ohlcv_schema, partition_columns)
    logger.info('Initialized ohlcv_raw table with seed data.')

    intervals = ['1h', '4h'] # '1d', '1w']
    for interval in intervals:
        coins_delta_lake_repository.initialize_table(f'ohlcv_{interval}', ohlcv_schema, partition_columns)
        logger.info(f'Initialized table ohlcv_{interval} with seed data.')



def generate_dummy_data():
    data = []
    current_time = datetime.datetime.utcnow().replace(microsecond=0)
    timestamp = int(current_time.timestamp() * 1000) 
    date_str = current_time.strftime('%Y-%m-%d')
    for coin in COINS:
        open_price = random.uniform(1000, 50000)
        close_price = open_price + random.uniform(-500, 500)
        high_price = max(open_price, close_price) + random.uniform(0, 500)
        low_price = min(open_price, close_price) - random.uniform(0, 500)
        volume = random.uniform(100, 10000)
        data.append({
            'coin': coin,
            'timestamp': timestamp,
            'date': date_str,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume,
        })
    return data, current_time

@aiocron.crontab('*/1 * * * *', start=True)
async def data_ingestion_job():
    logger.info('\n\nStarting data ingestion job.')
    raw_data, current_time = generate_dummy_data()
    df = pd.DataFrame.from_records(raw_data)
    coins_delta_lake_repository.write_to_table('ohlcv_raw', df)

    # intervals = [
    #     ('1h', datetime.timedelta(hours=1)),
    #     ('4h', datetime.timedelta(hours=4)),
    #     ('1d', datetime.timedelta(days=1)),
    #     ('1w', datetime.timedelta(weeks=1)),
    # ]
    intervals = [
        ('1h', datetime.timedelta(minutes=2)),
        ('4h', datetime.timedelta(minutes=4)),
        # ('1d', datetime.timedelta(minutes=5)),
        # ('1w', datetime.timedelta(minutes=20)),
    ]
    for interval_name, interval_length in intervals:
        await update_interval_data(interval_name, interval_length, df, current_time)

async def update_interval_data(interval_name, interval_length, new_data_df, current_time):
    logger.info(f'Updating interval data for {interval_name}.')
    coin = COINS[0] 
    interval_start_time = current_time - (datetime.timedelta(
        seconds=interval_length.total_seconds()-1))
    filters = [
        ('timestamp', '>=', int(interval_start_time.timestamp() * 1000)),
        ('coin', '=', coin),
    ]

    try:
        existing_df = coins_delta_lake_repository.read_table(f'ohlcv_{interval_name}', filters=filters)
    except Exception as e:
        logger.error(f'Error reading interval data for {interval_name}: {e}')
        existing_df = pl.DataFrame()

    if not existing_df.is_empty():
        logger.info(f'Updating existing interval record for {interval_name}.')
        updated_df = update_interval_record(existing_df, new_data_df)
        
        timestamp = updated_df['timestamp'].iloc[0]
        
        coins_delta_lake_repository.update_table(
            f'ohlcv_{interval_name}',
            updated_df,
            primary_keys=['coin', 'timestamp'],
            predicate=f'timestamp  >= {timestamp}'
        )

    else:
        logger.info(f'Creating new interval record for {interval_name}.')
        new_interval_df = create_new_interval_record(current_time, interval_name, new_data_df)
        print("New interval record", new_interval_df)
        coins_delta_lake_repository.write_to_table(f'ohlcv_{interval_name}', new_interval_df, mode='append')

def update_interval_record(existing_df, new_data_df):
    new_data_pl = pl.from_pandas(new_data_df)
    updated_df = existing_df.join(
        new_data_pl,
        on=['coin'],
        how='left',
        suffix='_new'
    )
    updated_df = updated_df.with_columns([
        pl.when(pl.col('high_new') > pl.col('high')).then(pl.col('high_new')).otherwise(pl.col('high')).alias('high'),
        pl.when(pl.col('low_new') < pl.col('low')).then(pl.col('low_new')).otherwise(pl.col('low')).alias('low'),
        pl.col('close_new').alias('close'),
        (pl.col('volume') + pl.col('volume_new')).alias('volume'),
    ])

    updated_df = updated_df.drop(['open_new', 'high_new', 'low_new', 'close_new', 'volume_new', 'timestamp_new', 'date_new'])
    updated_df = updated_df.to_pandas()
    return updated_df

def create_new_interval_record(interval_start_time, interval_name, new_data_df):
    # interval_end_time = interval_start_time + {
    #     '1h': datetime.timedelta(hours=1),
    #     '4h': datetime.timedelta(hours=4),
    #     '1d': datetime.timedelta(days=1),
    #     '1w': datetime.timedelta(weeks=1),
    # }[interval_name]

    interval_end_time = interval_start_time + {
        '1h': datetime.timedelta(minutes=2),
        '4h': datetime.timedelta(minutes=4),
        # '1d': datetime.timedelta(minutes=5),
        # '1w': datetime.timedelta(minutes=20),
    }[interval_name]



    df = new_data_df

    if df.shape[0] == 0:
        logger.warning(f'No data to create new interval record for {interval_name}.')
        return pl.DataFrame()
    aggregated_df = df.groupby('coin').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).reset_index()
    aggregated_df['timestamp'] = int(interval_start_time.timestamp() * 1000)
    aggregated_df['date'] = interval_start_time.strftime('%Y-%m-%d')
    return aggregated_df


def main():
    initialize_tables()
    logger.info('Starting the scheduler.')
    logger.info("Start time:", datetime.datetime.now())
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Shutting down.')
    finally:
        loop.close()

if __name__ == '__main__':
    main()