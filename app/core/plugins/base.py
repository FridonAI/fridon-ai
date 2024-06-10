from functools import reduce
from typing import Literal

from pydantic.v1 import BaseModel

from app.core.plugins.tools import BaseTool


class BasePlugin(BaseModel):
    name: str
    description: str
    tools: list[BaseTool]
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    type: Literal["subscription", "nft"] = "subscription"
    price: float | int = 0
    image_url: str | None = None

    @property
    def examples(self) -> list[str]:
        examples = reduce(lambda a, b: a + b, [tool.examples for tool in self.tools], [])
        return examples

    @property
    def examples_as_str(self) -> str:
        return "\n".join(self.examples)

    @property
    def slug(self) -> str:
        def slugify(text):
            import re
            import unicodedata
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('ascii')
            text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
            text = re.sub(r'[\s-]+', '-', text.strip().lower())
            return text
        return slugify(self.name)

    def full_description(self, tool_descriptions=True):
        description = "Name: " + self.name + " - " + self.description
        if tool_descriptions:
            description += "\n Here are following functionalities of this plugin: \n"
            for tool in self.tools:
                description += "\t" + tool.name + ": " + tool.description + "\n"
        description += "Examples: \n" + self.examples_as_str
        return description

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "slug": self.slug,
            "imageUrl": self.image_url,
            "description": self.description,
            "type": self.type,
            "owner": self.owner,
            "examples": self.examples,
            "functions": [tool.to_json() for tool in self.tools],
            "price": self.price
        }
