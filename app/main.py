import asyncio
import json

from dependency_injector.wiring import Provide, inject

from app import services
from app.containers import Container
from app.schema import ResponseDto
from app.utils import redis


@inject
async def handler(
    sub: redis.Subscription = Provide["subscription"],
    pub: redis.Publisher = Provide["publisher"],
    service: services.ProcessUserMessageService = Provide["process_user_message_service"],
):
    async for request in sub.channel("chat_message_created"):
        print(f"(Handler) Message Received: {request}")
        response_message = await service.process(request.chat_id, request.user.wallet_id, request.data.message)

        response = ResponseDto.parse_obj(
            {
                'chatId': request.chat_id,
                'user': {
                    'walletId': request.user.wallet_id
                },
                'data': {
                    'message': response_message
                },
                'aux': request.aux
            }
        )

        await pub.publish("response_received", str(response))


if __name__ == "__main__":
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", None)
    container.init_resources()
    container.wire(modules=[__name__])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(handler())