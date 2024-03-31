import torch


def convert_history_to_tensor(history: list[dict]) -> torch.Tensor:
    return torch.Tensor([item["value"] for item in history])
