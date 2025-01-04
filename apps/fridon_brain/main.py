import asyncio
import json

from dependency_injector.wiring import Provide, inject

from apps.fridon_brain import _preload_modules
from apps.fridon_brain.containers import Container
from apps.fridon_brain.services import (
    CalculateUserMessageScoreService,
    ProcessUserMessageService,
)
from fridonai_core.plugins.registry import ensure_plugin_registry
from libs.utils import redis
from libs.utils.redis.schemas import ResponseMessage


async def task_runner(
    request,
    service: ProcessUserMessageService,
    scorer_service: CalculateUserMessageScoreService,
    pub: redis.Publisher,
):
    plugins = [
        "coin-technical-chart-searcher",
        "coin-technical-analyzer",
        "coin-observer",
        "wallet",
        "jupiter", 
        "fridon",
        "solana-bonk-educator",
        "emperor-trading"
    ]
    response_message, used_agents = await service.process(
        request.user.wallet_id, request.chat_id, plugins, request.data.message
    )


    def _get_structured_answer(answer) -> dict:
        answer = json.loads(answer)
        if answer.get("source") == 'local':
            with open(answer.get("path"), 'r') as f:
                return {
                    "id": answer.get("name"),
                    "data": json.load(f)
                }
        return answer

    response = ResponseMessage.model_validate(
        {
            "chat_id": request.chat_id,
            "user": {"wallet_id": request.user.wallet_id},
            "data": {
                "message": response_message.text_answer,
                "structured_messages": [json.dumps(_get_structured_answer(ans)) for ans in response_message.structured_answers] if response_message.structured_answers else [],
                "message_id": request.data.message_id,
                "plugins_used": used_agents,
                "serialized_transaction": None,
            },
            "aux": request.aux,
        }
    )

    await pub.publish("response_received", str(response))

    score = await scorer_service.process(
        request.user.wallet_id, request.data.message, response_message, used_agents
    )
    print("Score:", score)
    await pub.publish(
        "scores_updated",
        json.dumps(
            {
                "chatId": request.chat_id,
                "walletId": request.user.wallet_id,
                "score": round(score, 2),
                "pluginsUsed": used_agents,
            }
        ),
    )


@inject
async def user_message_handler(
    sub: redis.Subscription = Provide["subscription"],
    pub: redis.Publisher = Provide["publisher"],
    service: ProcessUserMessageService = Provide["process_user_message_service"],
    scorer_service: CalculateUserMessageScoreService = Provide[
        "calculate_user_message_score_service"
    ],
):
    async for request in sub.channel("chat_message_created"):
        print(f"(Handler) Message Received: {request}")
        task = asyncio.create_task(task_runner(request, service, scorer_service, pub))


@inject
async def send_plugins(pub: redis.Publisher = Provide["publisher"]):
    registry = ensure_plugin_registry()
    plugins = [plugin_cls().to_json() for plugin_cls in registry.plugins.values()]

    for i, plugin in enumerate(plugins):
        if plugin["slug"] == "solana-bonk-educator":
            plugins.insert(0, plugins.pop(i))
            plugins[1], plugins[2] = plugins[2], plugins[1]
            break

    while True:
        await pub.publish("plugins", json.dumps(plugins), log=False)
        await asyncio.sleep(5)


if __name__ == "__main__":
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", "localhost")
    container.config.redis_password.from_env("REDIS_PASSWORD", None)
    container.init_resources()

    _preload_modules()

    loop = asyncio.get_event_loop()
    user_task = loop.create_task(user_message_handler())
    plugins_sender = loop.create_task(send_plugins())

    loop.run_until_complete(asyncio.gather(user_task, plugins_sender))

    loop.close()
