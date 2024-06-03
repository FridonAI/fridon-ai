import os
import uuid
from typing import Any

import aiohttp
from dependency_injector.wiring import Provide
from pydantic.v1 import Field

from app.core.plugins.utilities.base import BaseUtility
from app.schema import ResponseDto
from app.utils.redis import Publisher, QueueGetter


class BlockchainUtility(BaseUtility):
    request_url: str = Field(
        default=f"{os.environ.get('API_URL', 'hesoiam')}/blockchain/defi-operation",
        exclude=True,
    )

    pub: Publisher = Field(default=Provide["publisher"], exclude=True)

    queue_getter: QueueGetter = Field(default=Provide["queue_getter"], exclude=True)

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
        self, tx: dict | None, wallet_id: str, chat_id: str
    ) -> str:
        queue_name = str(uuid.uuid4())

        await self.pub.publish(
            "response_received",
            str(ResponseDto.from_params(chat_id, wallet_id, None, tx, queue_name, {})),
        )

        print("Waiting for response", queue_name)
        response = await self.queue_getter.get(queue_name=queue_name)
        print("Got Response", response)
        return response

    async def arun(self, *args, wallet_id: str, chat_id: str, **kwargs) -> dict | str | Any:
        request = self._arun(*args, **kwargs)
        request["args"]["walletAddress"] = wallet_id

        tx = await self._generate_tx(request)
        result = await self._send_and_wait(tx, wallet_id, chat_id)

        return result
