import json
import os
import uuid
import requests


from dependency_injector.wiring import Provide
from pydantic.v1 import BaseModel, root_validator

from app.schema import ResponseDto
from app.utils.redis import Publisher


class BaseUtility(BaseModel):
    name: str
    description: str

    @root_validator
    def validate_environment(cls, values: dict) -> dict:
        return values

    def run(self, *args, **kwargs) -> str: ...


class BlockchainUtility(BaseUtility):
    request_url: str = f"{os.environ['API_URL']}/blockchain/defi-operation",
    pub: Publisher = Provide["publisher"],
    queue_getter = Provide["queue_getter"],

    def _generate_tx(self, request):
        resp = requests.post(self.request_url, json=request).json()

        if "statusCode" in resp:
            if 500 > resp["statusCode"] >= 400:
                return resp.get("message", "Something went wrong!")
            if resp["statusCode"] >= 500:
                return "Something went wrong! Please try again later."

        return resp["data"]["serializedTx"]

    async def _send_and_wait(self, tx, chat_id, wallet_id):
        queue_name = str(uuid.uuid4())

        await self.pub.publish(
            "response_received",
            str(ResponseDto.from_params(
                chat_id,
                wallet_id,
                None,
                tx,
                queue_name,
                {}))
        )

        print("Waiting for response", queue_name)
        response = await self.queue_getter.get(queue_name=queue_name)
        print("Got Response", response)
        return response


class RemoteUtility(BaseUtility):
    request_url: str = f"{os.environ['API_URL']}/blockchain/points"

    def _get_remote_response(self, request):
        response = requests.post(self.request_url, json=request).json()
        if "statusCode" in response:
            if 500 > response["statusCode"] >= 400:
                return response.get("message", "Something went wrong!")
            if response["statusCode"] >= 500:
                return "Something went wrong! Please try again later."
        print("Got Response", response)
        return json.dumps(response['data'])
