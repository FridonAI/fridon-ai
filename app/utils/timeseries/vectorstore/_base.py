import torch

from app.utils.timeseries import TimeSeriesEmbeddings, TimeSeriesDataset, TimeSeriesDataLoader
from app.utils.timeseries import BaseTimeSeriesIndex


class TimeSeriesVectorStore:
    def __init__(self, embeddings: TimeSeriesEmbeddings, index: BaseTimeSeriesIndex):
        self._embeddings = embeddings
        self._index = index

    def embed(self, data: torch.Tensor | list[torch.Tensor]) -> torch.Tensor:
        return self._embeddings(data)

    def search(self, search_vector: torch.Tensor, top_k: int) -> list[tuple[str, float]]:
        return self._index.query(search_vector.reshape(-1).tolist(), top_k)

    def load_dataset(self, dataset: TimeSeriesDataset) -> None:
        for batch in TimeSeriesDataLoader(dataset):
            vector = self.embed([t.data for t in batch])
            symbols = [t.symbol for t in batch]
            self._index.upsert(zip(symbols, vector))
