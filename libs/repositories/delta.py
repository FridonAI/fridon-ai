from datetime import datetime
import logging
import os
from typing import Any, Literal

import polars as pl
import pyarrow as pa
import pyarrow.compute as pc
from deltalake import DeltaTable, write_deltalake
from pyarrow.compute import Expression
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _initialize_storage_options() -> dict[str, str]:
    return {
        # "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", ""),
        # "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        # "AWS_REGION": os.getenv("AWS_DEFAULT_REGION", ""),
    }


class DeltaRepository(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    table_schema: pa.Schema = Field(...)
    table_name: str = Field(...)
    partition_columns: list[str] = Field(...)
    storage_options: dict[str, str] = Field(default_factory=_initialize_storage_options)

    @property
    def s3_path(self) -> str:
        return f"s3://{os.getenv('S3_BUCKET_NAME')}/{self.table_name}"

    def _check_table_exists(self) -> bool:
        return DeltaTable.is_deltatable(
            self.s3_path, storage_options=self.storage_options
        )

    def read(
        self,
        *,
        partitions: list[tuple[str, str, Any]] | None = None,
        columns: list[str] | None = None,
        filters: Expression | None = None,
        last_n: int | None = None,
        order_by: str | None = None,
    ) -> pl.DataFrame:
        if not self._check_table_exists():
            logger.error(f"Table {self.table_name} does not exist at {self.s3_path}")
            raise FileNotFoundError(
                f"Table {self.table_name} does not exist at {self.s3_path}"
            )

        try:
            dt = DeltaTable(self.s3_path, storage_options=self.storage_options)

            arrow_table = dt.to_pyarrow_table(
                partitions=partitions, columns=columns, filters=filters
            )
            result = pl.from_arrow(arrow_table).sort(order_by)
            if last_n is not None:
                if order_by is None:
                    logger.warning(
                        "order_by is not specified. Using descending order by timestamp."
                    )
                    order_by = self.table_schema.names[0]
                result = result.tail(last_n)
            logger.info(f"Table {self.table_name} read successfully.")
        except Exception as e:
            logger.error(f"Error reading table {self.table_name}: {e}")
            raise
        return result if isinstance(result, pl.DataFrame) else result.to_frame()

    def write(
        self, df: pl.DataFrame, mode: Literal["append", "overwrite"] = "append"
    ) -> None:
        if not self._check_table_exists():
            logger.info(f"Table {self.table_name} does not exist at {self.s3_path}")
            logger.info(f"Initializing table {self.table_name} at {self.s3_path}")
            self._initialize_table()

        try:
            write_deltalake(
                self.s3_path,
                df.to_pandas(),
                schema=self.table_schema,
                partition_by=self.partition_columns,
                storage_options=self.storage_options,
                mode=mode,
            )
            logger.info(f"Data written to table {self.table_name} successfully.")
        except Exception as e:
            logger.error(f"Error writing to table {self.table_name}: {e}")
            raise

    def _initialize_table(self) -> None:
        logger.info(
            f"Initializing table {self.table_name} at {self.s3_path}."
        )
        try:
            DeltaTable.create(
                table_uri=self.s3_path,
                mode="ignore",
                schema=self.table_schema,
                partition_by=self.partition_columns,
                storage_options=self.storage_options,
            )
            logger.info(f"Table {self.table_name} initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing table {self.table_name}: {e}")
            raise

    def update(
        self,
        df: pl.DataFrame,
        *,
        predicate: str,
        source_alias: str = "s",
        target_alias: str = "t",
    ) -> None:
        if not self._check_table_exists():
            self.write(df)
            return

        try:
            dt = DeltaTable(self.s3_path, storage_options=self.storage_options)
            (
                dt.merge(
                    source=df.to_pandas(),
                    predicate=predicate,
                    source_alias=source_alias,
                    target_alias=target_alias,
                )
                .when_matched_update_all()
                .when_not_matched_insert_all()
                .execute()
            )
            logger.info(f"Table {self.table_name} updated successfully with {df.shape[0]} rows.")
        except Exception as e:
            logger.error(f"Error updating table {self.table_name}: {e}")
            raise

    def get_records_in_time_range(
            self,
            start: datetime,
            end: datetime,
            filters: Expression | None = None,
            number_of_points: int | None = 50,
            order_by: str = "timestamp",
            columns: list[str] = None
        ) -> pl.DataFrame:

        full_filters = (pc.field("timestamp") >= int((start).timestamp() * 1000)) & (pc.field("timestamp") <= int((end).timestamp() * 1000))
        if filters is not None:
            full_filters = filters & full_filters

        df = self.read(
            filters=full_filters,
            columns=columns,
            last_n=number_of_points,
            order_by=order_by)

        return df
