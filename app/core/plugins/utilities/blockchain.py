import uuid
from typing import Any

import aiohttp
from dependency_injector.wiring import Provide
from pydantic.v1 import Field

from app.core.plugins.utilities.base import BaseUtility
from app.schema import ResponseDto
from app.settings import settings
from app.utils.redis import Publisher, QueueGetter


class BlockchainUtility(BaseUtility):
    request_url: str = Field(
        default=f"{settings.API_URL}/data/executor",
        exclude=True,
    )

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
            pub: Publisher = Provide["publisher"],
            queue_getter: QueueGetter = Provide["queue_getter"],
    ) -> str:
        queue_name = str(uuid.uuid4())

        await pub.publish(
            "response_received",
            str(ResponseDto.from_params(chat_id, wallet_id, None, tx, queue_name, {})),
        )

        print("Waiting for response", queue_name)
        response = await queue_getter.get(queue_name=queue_name)
        print("Got Response", response)
        return response

    async def arun(self, *args, chat_id: str, **kwargs) -> dict | str | Any:
        request = await self._arun(*args,  **kwargs)

        tx = await self._generate_tx(request)
        result = await self._send_and_wait(tx, kwargs.get("wallet_id", ""), chat_id)

        return result

    class Config:
        arbitrary_types_allowed = True
