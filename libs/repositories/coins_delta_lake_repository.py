import polars as pl
from deltalake import DeltaTable, write_deltalake
import pyarrow as pa
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


storage_options = {}
storage_options["AWS_ACCESS_KEY_ID"] = os.getenv('AWS_ACCESS_KEY_ID')
storage_options["AWS_SECRET_ACCESS_KEY"] = os.getenv('AWS_SECRET_ACCESS_KEY')
storage_options["AWS_S3_ALLOW_UNSAFE_RENAME"] = "true"
storage_options["AWS_REGION"] = 'eu-central-1'
storage_options["AWS_S3_ALLOW_UNSAFE_RENAME"] = "true"

S3_BUCKET_NAME = os.getenv('S3_DATA_BUCKET_NAME', 'fridon-ai-coin-data')


S3_BASE_PATH = f's3://{S3_BUCKET_NAME}'

def initialize_table(table_name: str, schema: pa.Schema, partition_columns: list = None):
    """
    Initializes a Delta Lake table with the given schema and partitions.
    """
    table_path = f'{S3_BASE_PATH}/{table_name}'
    try:
        DeltaTable.create(
            table_uri=table_path,
            mode='ignore',
            schema=schema,
            partition_by=partition_columns,
            storage_options=storage_options
        )
        logger.info(f'Table {table_name} initialized successfully.')
    except Exception as e:
        logger.error(f'Error initializing table {table_name}: {e}')
        raise


def write_to_table(table_name: str, df: pl.DataFrame, mode='append'):
    """
    Writes data to the specified Delta Lake table.

    Parameters:
    - table_name: Name of the Delta Lake table.
    - df: Polars DataFrame containing the data to write.
    - mode: Write mode ('append', 'overwrite', etc.).
    """
    table_path = f'{S3_BASE_PATH}/{table_name}'
    try:
        write_deltalake(
            table_path,
            df,
            mode=mode,
            partition_by=['date', 'timestamp'],
            storage_options=storage_options
        )
        logger.info(f'Data written to table {table_name} successfully.')
    except Exception as e:
        logger.error(f'Error writing to table {table_name}: {e}')
        raise

def read_table(table_name: str, columns=None, partitions=None, filters=None) -> pl.DataFrame:
    """
    Reads data from the specified Delta Lake table.

    Parameters:
    - table_name: Name of the Delta Lake table.
    - columns: List of columns to read (optional).

    Returns:
    - Polars DataFrame with the table data.
    """
    table_path = f'{S3_BASE_PATH}/{table_name}'
    try:
        dt = DeltaTable(table_path, storage_options=storage_options)
        arrow_table = dt.to_pyarrow_table(columns=columns, partitions=partitions, filters=filters)
        df = pl.from_arrow(arrow_table)
        logger.info(f'Table {table_name} read successfully.')
        return df
    except Exception as e:
        logger.error(f'Error reading table {table_name}: {e}')
        raise

def update_table(table_name: str, df: pl.DataFrame, primary_keys: list, predicate: str = None):
    """
    Updates existing records in the Delta Lake table based on primary keys.

    Parameters:
    - table_name: Name of the Delta Lake table.
    - df: Polars DataFrame containing the updated data.
    - primary_keys: List of columns that form the primary key.
    """
    table_path = f'{S3_BASE_PATH}/{table_name}'

    try:
        dt = DeltaTable(table_path, storage_options=storage_options)
        (
            dt.merge(
                source=df,
                predicate="s.timestamp = t.timestamp",
                source_alias="s",
                target_alias="t",
            )
            .when_matched_update_all()
            .when_not_matched_insert_all()
                .execute()
        )

        logger.info(f'Table {table_name} updated successfully. predicate: {predicate}')
    except Exception as e:
        logger.error(f'Error updating table {table_name}: {e} predicate: {predicate}')
        raise

