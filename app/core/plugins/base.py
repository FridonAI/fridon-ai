from functools import reduce
from typing import Literal

from pydantic.v1 import BaseModel

from app.core.plugins.tools import BaseTool


class BasePlugin(BaseModel):
    name: str
    description: str
    tools: list[BaseTool]
    owner: str
    type: Literal["subscription", "nft"] = "subscription"
    price: float = .0

    @property
    def examples(self) -> list[str]:
        examples = reduce(lambda a, b: a + b, [tool.examples for tool in self.tools], [])
        return examples

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "examples": self.examples,
            "functions": [tool.to_json() for tool in self.tools],
            "price": self.price
        }
