import torch
from chronos import ChronosPipeline as BaseChronosPipeline

from app.utils.chronos.utils import mean_pooling


class ChronosPipeline(BaseChronosPipeline):
    @torch.no_grad()
    def embed_mean(
            self,
            context: torch.Tensor | list[torch.Tensor]
    ) -> torch.Tensor:
        context = self._prepare_and_validate_context(context)
        token_ids, attention_mask, tokenizer_state = self.tokenizer.input_transform(context)
        embeddings = self.model(
            input_ids=token_ids.to(self.model.device),
            attention_mask=attention_mask.to(self.model.device),
        )
        mean_embeddings = mean_pooling(embeddings, attention_mask)
        return mean_embeddings.cpu()
