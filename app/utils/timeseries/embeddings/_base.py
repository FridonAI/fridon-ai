import torch

from app.utils.chronos import ChronosPipeline


class TimeSeriesEmbeddings:
    AVAILABLE_MODELS = [
        "amazon/chronos-t5-tiny",
        "amazon/chronos-t5-mini",
        "amazon/chronos-t5-small",
        "amazon/chronos-t5-base",
        "amazon/chronos-t5-large",
    ]

    def __init__(self, model_name: str, device: str = "cpu"):
        if not self._verify_model(model_name):
            raise ValueError(f"Model {model_name} is not available.")

        self.pipeline = ChronosPipeline.from_pretrained(
            model_name,
            device_map=device,
            torch_dtype=torch.bfloat16,
        )

    def __call__(self, context: torch.Tensor | list[torch.Tensor]) -> torch.Tensor:
        return self.pipeline.embed_mean(context)

    @classmethod
    def _verify_model(cls, model_name: str) -> bool:
        return model_name in cls.AVAILABLE_MODELS
