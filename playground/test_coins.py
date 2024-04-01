from typing import Iterator

import torch
from dotenv import load_dotenv

from app.utils.birdeye import BirdEyeApiClient, BirdEyeDataset, convert_history_to_tensor
from app.utils.timeseries import PineconeTimeSeriesIndex
from app.utils.timeseries import TimeSeriesDataset, TimeSeriesData
from app.utils.timeseries import TimeSeriesEmbeddings
from app.utils.timeseries import TimeSeriesVectorStore
from datetime import datetime, timedelta

load_dotenv()


class YFinanceDataset(TimeSeriesDataset):
    def __init__(self, symbols: list[str]):
        super().__init__(symbols)

    def __iter__(self) -> Iterator[TimeSeriesData]:
        for symbol in self.symbols:
            yield TimeSeriesData(symbol, torch.randn(100))


if __name__ == "__main__":
    birdeye_api = BirdEyeApiClient(base_url="https://public-api.birdeye.so/defi", api_key="9f0fc8d9eb0f42758e36ea3f71bec8d6")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    token_list = [
        {
            "symbol": "SOL1",
            "address": "So11111111111111111111111111111111111111112",
        },
        {
            "symbol": "SOL2",
            "address": "So11111111111111111111111111111111111111112",
        }
    ]

    dataset = BirdEyeDataset(token_list, birdeye_api, int(start_date.timestamp()), int(end_date.timestamp()), "1H")

    embeddings = TimeSeriesEmbeddings("amazon/chronos-t5-tiny")
    index = PineconeTimeSeriesIndex("embeddings-chronos-t5-tiny", 256)
    vector_store = TimeSeriesVectorStore(embeddings, index)
    # vector_store.load_dataset(dataset)

    solana_tensor = convert_history_to_tensor(birdeye_api.get_history(token_list[0]["address"], int(start_date.timestamp()), int(end_date.timestamp()), "1H"))
    print(vector_store.search(vector_store.embed(solana_tensor), top_k=5))


