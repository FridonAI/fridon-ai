import json
import os
from typing import Any

import aiohttp
from pydantic.v1 import Field

from app.core.plugins.utilities.base import BaseUtility


class RemoteUtility(BaseUtility):
    request_url: str = Field(
        default=f"{os.environ.get('API_URL', 'hesoiam')}/blockchain/points",
        exclude=True
    )

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
                return json.dumps(data['data'])

    async def arun(self, *args, **kwargs) -> dict | str | Any:
        request = await self._arun(*args, **kwargs)

        return self._get_remote_response(request)
