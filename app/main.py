import asyncio

from dependency_injector.wiring import Provide, inject

from app.services import ProcessUserMessageService
from app.containers import Container
from app.schema import ResponseDto
from app.utils import redis


async def task_runner(
        request,
        service: ProcessUserMessageService,
        pub: redis.Publisher
):
    response_message = await service.process(request.user.wallet_id, request.chat_id, request.data.personality, request.data.message)
    response = ResponseDto.parse_obj(
        {
            'chat_id': request.chat_id,
            'user': {
                'wallet_id': request.user.wallet_id
            },
            'data': {
                'message': response_message,
                'serialized_transaction': None
            },
            'aux': request.aux
        }
    )
    await pub.publish("response_received", str(response))


@inject
async def user_message_handler(
    sub: redis.Subscription = Provide["subscription"],
    pub: redis.Publisher = Provide["publisher"],
    service: ProcessUserMessageService = Provide["process_user_message_service"],
):

    async for request in sub.channel("chat_message_created"):
        print(f"(Handler) Message Received: {request}")
        task = asyncio.create_task(task_runner(request, service, pub))


@inject
async def send_plugins(
    pub: redis.Publisher = Provide["publisher"]
):
    for _ in range(36):
        await pub.publish("plugins", [])
        await asyncio.sleep(5)


if __name__ == "__main__":
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", None)
    container.init_resources()
    container.wire(modules=[__name__, "app.adapters.blockchain", "app.services.process_user_message_service"])

    loop = asyncio.get_event_loop()
    user_task = loop.create_task(user_message_handler())
    plugins_sender = loop.create_task(send_plugins())

    loop.run_until_complete(asyncio.gather(user_task, plugins_sender))

    loop.close()



