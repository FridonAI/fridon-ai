import polars as pl
import pyarrow.compute as pc
from pyarrow.compute import Expression
from datetime import datetime, timedelta, UTC

from libs.repositories.delta import DeltaRepository



class CoinsRepository(DeltaRepository):
    interval_to_delta: dict[str, timedelta] = {
        "raw": timedelta(minutes=30),
        "1h": timedelta(hours=1),
        "4h": timedelta(hours=4),
        "1d": timedelta(days=1),
        "1w": timedelta(days=7),
    }

    @property
    def interval(self) -> str:
        return self.table_name.split("_")[-1]

    def get_coin_latest_record(self, coin_name: str, filters = None, columns: list[str] = None) -> pl.DataFrame: 
        if filters is None:
            return self.get_the_latest_records((pc.field("coin") == coin_name), columns)
        return self.get_the_latest_records((pc.field("coin") == coin_name) & filters, columns)


    def get_coin_last_records(self, coin_name: str, number_of_points: int = 50, filters = None, columns: list[str] = None) -> pl.DataFrame:
        if filters is None:
            return self.get_last_records((pc.field("coin") == coin_name), number_of_points, columns)
        return self.get_last_records((pc.field("coin") == coin_name) & filters, number_of_points, columns)
    

    def get_coin_records_in_time_range(self, coin: str, start: datetime, end: datetime, filters = None, columns: list[str] = None) -> pl.DataFrame:
        if filters is None:
            return self.get_records_in_time_range((pc.field("coin") == coin), start, end, columns)
        return self.get_records_in_time_range((pc.field("coin") == coin) & filters, start, end, columns)
    

    def get_the_latest_records(self, filters: Expression, columns: list[str] = None) -> pl.DataFrame:
        df = self.get_last_records(filters, number_of_points=1, columns=columns)
        return df.sort("timestamp").group_by("coin").agg(pl.all().last())

    def get_last_records(self, filters: Expression, number_of_points: int = 50, columns: list[str] = None) -> pl.DataFrame:
        delta = self.interval_to_delta[self.interval]
        return self.get_records_in_time_range(
            filters, 
            datetime.now(UTC) - delta * (number_of_points + 1), 
            datetime.now(UTC), 
            number_of_points=number_of_points, 
            columns=columns
        )
