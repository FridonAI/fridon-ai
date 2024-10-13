import pyarrow as pa
from libs.repositories.coins import CoinsRepository


class OhlcvRepository(CoinsRepository):
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
        ]
    )
    partition_columns: list[str] = ["date", "timestamp"]
