import pyarrow as pa
from libs.repositories.coins import CoinsRepository


class IndicatorsRepository(CoinsRepository):
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
