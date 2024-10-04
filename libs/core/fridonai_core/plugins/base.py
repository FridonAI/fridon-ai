from functools import reduce
from typing import Literal

from pydantic import BaseModel

from fridonai_core.plugins.tools import BaseTool


class BasePlugin(BaseModel):
    name: str
    description: str
    tools: list[BaseTool]
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    type: Literal["subscription", "nft"] = "subscription"
    price: float | int = 0
    image_url: str | None = None
    exclude: bool = False
    json_format: bool = False

    @property
    def examples(self) -> list[dict]:
        examples = reduce(lambda a, b: a + b, [tool.examples for tool in filter(lambda x: x.helper is False, self.tools)], [])
        return examples

    @property
    def request_examples(self) -> list[str]:
        return [example["request"] for example in self.examples]

    @property
    def examples_as_str(self) -> str:
        return "\n".join(self.request_examples)

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
        description = self.name + " - " + self.description
        if tool_descriptions:
            description += "\n Here are following functionalities of this plugin: \n"
            for tool in filter(lambda x: x.helper is False, self.tools):
                description += "\t" + tool.name + ": " + tool.description + "\n"
        description += "Examples: \n" + self.examples_as_str
        return description

    @property
    def output_format(self):
        if self.json_format:
            return "\n After using tools and having everything together, and `plugin_status` going to be True, that means tool done successfully what asked to be done, copy whole tool's answer response as json string in CompleteTool's answer. If it didn't went good generate explanatory text from output. \n"
        else:
            return "\n After using tools and having everything together, combine all tool's answer responses in CompleteTool's answer as a text. \n"

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
