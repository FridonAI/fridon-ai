from typing import Any

from pydantic import BaseModel


class Adapter(BaseModel):
    def send(self, topic, params, *args, **kwargs) -> dict | str | Any: ...
