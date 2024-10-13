import pyarrow as pa
import polars as pl
import pyarrow.compute as pc
from datetime import datetime, timedelta, UTC
from libs.repositories.delta import DeltaRepository


class IndicatorsRepository(DeltaRepository):
    table_schema: pa.Schema = pa.schema(
        [
            ("coin", pa.string()),
            ("timestamp", pa.int64()),
            ("date", pa.string()),
            ("open", pa.float64()),
            ("high", pa.float64()),
            ("low", pa.float64()),
            ("close", pa.float64()),
            ("volume", pa.float64()),
            ("MACD_12_26_9", pa.float64()),
            ("MACD_histogram_12_26_9", pa.float64()),
            ("RSI_14", pa.float64()),
            ("BBL_5_2.0", pa.float64()),
            ("BBM_5_2.0", pa.float64()),
            ("BBU_5_2.0", pa.float64()),
            ("SMA_20", pa.float64()),
            ("EMA_50", pa.float64()),
            ("OBV_in_million", pa.float64()),
            ("STOCHk_14_3_3", pa.float64()),
            ("STOCHd_14_3_3", pa.float64()),
            ("ADX_14", pa.float64()),
            ("WILLR_14", pa.float64()),
            ("CMF_20", pa.float64()),
            ("PSARl_0.02_0.2", pa.float64(), True),
            ("PSARs_0.02_0.2", pa.float64(), True),
        ]
    )
    partition_columns: list[str] = ["date", "timestamp"]

    def get_coin_latest_record(self, coin_name: str, interval: str, filters = None) -> pl.DataFrame: 
        if filters is None:
            return self.get_the_latest_records((pc.field("coin") == coin_name), interval)
        return self.get_the_latest_records((pc.field("coin") == coin_name) & filters, interval)


    def get_coin_last_records(self, coin_name: str, interval: str, number_of_points: int = 100, filters = None) -> pl.DataFrame:
        if filters is None:
            return self.get_last_records((pc.field("coin") == coin_name), interval, number_of_points)
        return self.get_last_records((pc.field("coin") == coin_name) & filters, interval, number_of_points)
    

    def get_coin_records_in_time_range(self, coin: str, start: datetime, end: datetime, filters = None) -> pl.DataFrame:
        if filters is None:
            return self.get_records_in_time_range((pc.field("coin") == coin), start, end)
        return self.get_records_in_time_range((pc.field("coin") == coin) & filters, start, end)
    

    def get_the_latest_records(self, filters: pl.Expr, interval: str) -> pl.DataFrame:
        df = self.get_last_records(filters, interval, number_of_points=1)
        return df.sort("timestamp").group_by("coin").agg(pl.all().last())

    def get_last_records(self, filters, interval: str, number_of_points: int = 100) -> pl.DataFrame:
        delta = {
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "1d": timedelta(days=1),
            "1w": timedelta(days=7),
        }[interval]

        return self.get_records_in_time_range(filters, datetime.now(UTC) - delta * number_of_points, datetime.now(UTC))

    def get_records_in_time_range(self, filters, start: datetime, end: datetime) -> pl.DataFrame:
        df = self.read(
            filters=filters
            & (pc.field("timestamp") >= int((start).timestamp() * 1000))
            & (pc.field("timestamp") <= int((end).timestamp() * 1000)))
        return df
