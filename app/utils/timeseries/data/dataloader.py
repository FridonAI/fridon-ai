from torch.utils.data import DataLoader

from app.utils.timeseries.data.dataset import TimeSeriesDataset


class TimeSeriesDataLoader(DataLoader):
    def __init__(self, dataset: TimeSeriesDataset, batch_size: int, **kwargs):
        super().__init__(dataset, batch_size=batch_size, collate_fn=lambda batch: batch, **kwargs)
