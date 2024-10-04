from typing import Any

from pydantic import BaseModel


class BaseAdapter(BaseModel):
    async def send(self, topic, params, *args, **kwargs) -> dict | str | Any: ...
