from dataclasses import dataclass

import torch


@dataclass
class TimeSeriesData:
    symbol: str
    data: torch.Tensor
