from typing import Iterator

from app.utils.birdeye import BirdEyeApiClient
from app.utils.birdeye.utils import convert_history_to_tensor
from app.utils.timeseries import TimeSeriesDataset, TimeSeriesData


class BirdEyeDataset(TimeSeriesDataset):
    def __init__(
            self,
            token_list: list,
            api_client: BirdEyeApiClient,
            time_from: int,
            time_to: int,
            interval: str = "1H"
    ) -> None:
        super(TimeSeriesDataset, self).__init__()
        self._token_list = token_list
        self._api_client = api_client
        self._time_from = time_from
        self._time_to = time_to
        self._interval = interval

    def __len__(self) -> int:
        return len(self._token_list)

    def __iter__(self) -> Iterator[TimeSeriesData]:
        for token in self._token_list:
            token_history = self._api_client.get_history(
                token["address"], 
                self._time_from, 
                self._time_to,
                self._interval
            )
            token_history_tensor = convert_history_to_tensor(token_history)
            yield TimeSeriesData(token["symbol"], token_history_tensor)
