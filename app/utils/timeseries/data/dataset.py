import abc
from typing import Iterator

import torch
from torch.utils.data import IterableDataset

from app.utils.timeseries.data.models import TimeSeriesData


class TimeSeriesDataset(IterableDataset, abc.ABC):

    def __init__(self, symbols: list[str]):
        self.symbols = symbols

    def __len__(self) -> int:
        return len(self.symbols)

    @abc.abstractmethod
    def __iter__(self) -> Iterator[TimeSeriesData]:
        raise NotImplementedError()
