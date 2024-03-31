from typing import List

from fastapi_camelcase import CamelModel


class Content(CamelModel):
    source: str
    author: str
    created_at: str
    content: str

    def __str__(self):
        return f"Source: {self.source} \n\n Author: {self.author} \n\n Content: {self.content} \n\n Created at: {self.created_at} \n\n\n"


class Media(CamelModel):
    description: str
    contents: List[Content]

