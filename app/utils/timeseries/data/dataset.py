import abc
from typing import Iterator

from torch.utils.data import IterableDataset

from app.utils.timeseries.data.models import TimeSeriesData


class TimeSeriesDataset(IterableDataset, abc.ABC):

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def __iter__(self) -> Iterator[TimeSeriesData]:
        raise NotImplementedError()
