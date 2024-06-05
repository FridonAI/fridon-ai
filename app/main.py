import asyncio
import json

from dependency_injector.wiring import Provide, inject

from app.core.plugins.registry import ensure_plugin_registry
from app.services import ProcessUserMessageService
from app.containers import Container
from app.schema import ResponseDto
from app.utils import redis


async def task_runner(
        request,
        service: ProcessUserMessageService,
        pub: redis.Publisher
):
    response_message, used_agents = await service.process(request.user.wallet_id, request.chat_id, request.data.plugins, request.data.message)
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
    await pub.publish("scores_updated", json.dumps({"chatId": request.chat_id, "walletId": request.user.wallet_id, "score": 10, "pluginsUsed": used_agents}))

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
    registry = ensure_plugin_registry()
    plugins = [plugin_cls().to_json() for plugin_cls in registry.plugins.values()]
    for _ in range(5):
        await pub.publish("plugins", json.dumps(plugins))
        await asyncio.sleep(5)


if __name__ == "__main__":
    from app.settings import settings
    print(settings.OPENAI_API_KEY)
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", None)
    container.init_resources()
    container.wire(modules=[__name__, "app.core.plugins.utilities.blockchain", "app.services.process_user_message_service"])

    loop = asyncio.get_event_loop()
    user_task = loop.create_task(user_message_handler())
    plugins_sender = loop.create_task(send_plugins())

    loop.run_until_complete(asyncio.gather(user_task, plugins_sender))

    loop.close()



