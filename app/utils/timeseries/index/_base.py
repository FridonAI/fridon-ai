import abc


class BaseTimeSeriesIndex(abc.ABC):

    @abc.abstractmethod
    def upsert(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def query(self, *args, **kwargs):
        raise NotImplementedError()
