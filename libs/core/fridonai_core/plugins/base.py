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
    price_currency: str = "PYUSD"
    image_url: str | None = None
    exclude: bool = False
    json_format: bool = False

    @property
    def examples(self) -> list[dict]:
        examples = reduce(lambda a, b: a + b, [tool.examples for tool in filter(lambda x: not x.helper, self.tools)], [])
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
        description = ""
        if tool_descriptions:
            description += "\nThese are tool descriptions of the plugin: \n"
            for tool in filter(lambda x: not x.helper, self.tools):
                description += "\t" + tool.name + ": " + tool.description + "\n"
        description += "\n *** Examples *** \n" + self.examples_as_str

        return description

    @property
    def output_format(self):
        if self.json_format:
            return "\n If tool's answer is json string copy it as it is otherwise use text response and dont mark is_json as true. \n"
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
