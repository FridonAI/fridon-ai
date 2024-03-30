import torch
import torch.nn.functional as F


def mean_pooling(embeddings: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    mean_embeddings = torch.sum(embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return F.normalize(mean_embeddings, p=2, dim=1)
