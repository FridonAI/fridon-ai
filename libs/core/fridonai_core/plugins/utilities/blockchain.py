from typing import Any, Optional

import aiohttp
from pydantic import Field

from fridonai_core.plugins.utilities.adapter_base import BaseAdapter
from fridonai_core.plugins.utilities.base import BaseUtility
from settings import settings


class BlockchainUtility(BaseUtility):
    request_url: str = Field(
        default=f"{settings.API_URL}/data/executor",
        exclude=True,
    )

    communicator: Optional[BaseAdapter] = Field(default=None, exclude=True)

    async def _generate_tx(self, request: dict[str, Any]) -> str | dict | Any:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.request_url, json=request) as resp:
                resp = await resp.json()
                if "statusCode" in resp:
                    if 500 > resp["statusCode"] >= 400:
                        return resp.get("message", "Something went wrong!")
                    if resp["statusCode"] >= 500:
                        return "Something went wrong! Please try again later."

                return resp["data"]["serializedTx"]

    async def _send_and_wait(
        self,
        tx: dict | None,
        wallet_id: str,
        chat_id: str,
    ) -> str:
        response = await self.communicator.send(
            "response_received",
            {
                "chat_id": chat_id,
                "wallet_id": wallet_id, 
                "tx": tx,
            }
        )
        print("Got Response", response)
        return response

    async def arun(self, *args, chat_id: str, **kwargs) -> str:
        request = await self._arun(*args, **kwargs)

        tx = await self._generate_tx(request)
        result = await self._send_and_wait(tx, kwargs.get("wallet_id", ""), chat_id)

        return result

    class Config:
        arbitrary_types_allowed = True
