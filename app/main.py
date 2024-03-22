import asyncio

from dependency_injector.wiring import Provide, inject

from app.services import ProcessUserMessageService, HandleFrontMessageService
from app.containers import Container
from app.schema import ResponseDto
from app.utils import redis


@inject
async def user_message_handler(
    sub: redis.Subscription = Provide["subscription"],
    pub: redis.Publisher = Provide["publisher"],
    service: ProcessUserMessageService = Provide["process_user_message_service"],
):
    async for request in sub.channel("chat_message_created"):
        print(f"(Handler) Message Received: {request}")
        response_message = await service.process(request.user.wallet_id, request.chat_id, request.data.message)

        response = ResponseDto.parse_obj(
            {
                'chat_id': request.chat_id,
                'user': {
                    'wallet_id': request.user.wallet_id
                },
                'data': {
                    'message': response_message
                },
                'aux': request.aux
            }
        )

        await pub.publish("response_received", str(response))


@inject
async def front_message_handler(
        sub: redis.Subscription = Provide["subscription"],
        service: HandleFrontMessageService = Provide["handle_front_message_service"],
):
    async for request in sub.channel("chat_message_info_created"):
        print(f"(Handler) Message Received: {request}")
        await service.handle(request.chat_id, request.data.message)


if __name__ == "__main__":
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", None)
    container.init_resources()
    container.wire(modules=[__name__, "app.adapters.blockchain"])

    loop = asyncio.get_event_loop()
    user_task = loop.create_task(user_message_handler())
    front_task = loop.create_task(front_message_handler())

    loop.run_until_complete(asyncio.gather(user_task, front_task))

    loop.close()



