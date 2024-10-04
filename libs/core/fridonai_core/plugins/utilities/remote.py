import json
from typing import Any

import aiohttp
from pydantic import Field

from fridonai_core.plugins.utilities.base import BaseUtility
from settings import settings


class RemoteUtility(BaseUtility):
    request_url: str = Field(default=f"{settings.API_URL}/data/executor", exclude=True)

    async def _get_remote_response(self, request):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.request_url, json=request) as response:
                data = await response.json()
                if "statusCode" in data:
                    if 500 > data["statusCode"] >= 400:
                        return data.get("message", "Something went wrong!")
                    if data["statusCode"] >= 500:
                        return "Something went wrong! Please try again later."
                print("Got Response", data)
                return json.dumps(data["data"])

    async def arun(self, *args, **kwargs) -> dict | str | Any:
        request = await self._arun(*args, **kwargs)
        return await self._get_remote_response(request)
