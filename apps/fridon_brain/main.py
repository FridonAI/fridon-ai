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
from libs.utils.redis.schemas import ResponseMessage, RequestMessage


def _send_literal_message(
    literal_client, thread_id, thread_name, message_type, message_name, message
):
    try:
        with literal_client.thread(thread_id=thread_id, name=thread_name) as _:
            literal_client.message(
                content=message, type=message_type, name=message_name
            )
    except Exception as e:
        print(f"Error sending message to literal: {e}")


async def _handle_score(
    request,
    scorer_service,
    pub,
    used_agents,
    response_message,
    prev_messages,
    new_used_agents_count,
):
    if (
        len(used_agents) == 0
        or used_agents[-1] == "off-topic"
        or new_used_agents_count == 0
    ):
        score = 0
    else:
        score = await scorer_service.process(
            request.user.wallet_id,
            request.data.message,
            response_message,
            used_agents[len(used_agents) - new_used_agents_count :],
            prev_user_messages=prev_messages,
        )
    print(
        "Score:",
        score,
        "New used agents:",
        used_agents[len(used_agents) - new_used_agents_count :],
    )
    await pub.publish(
        "scores_updated",
        json.dumps(
            {
                "chatId": request.chat_id,
                "walletId": request.user.wallet_id,
                "score": round(score, 2),
                "pluginsUsed": [
                    agent
                    for agent in used_agents[len(used_agents) - new_used_agents_count :]
                    if agent not in ["off-topic", "bonk-notifier", "fridon"]
                ],
            }
        ),
    )


async def task_runner(
    request: RequestMessage,
    service: ProcessUserMessageService,
    scorer_service: CalculateUserMessageScoreService,
    pub: redis.Publisher,
    literal_client,
):
    plugins = [
        "intelligent-coin-searcher",
        "coin-technical-analyzer",
        "coin-observer",
        "wallet",
        "fridon",
        "solana-bonk-educator",
        "og-traders-simulator",
        "off-topic",
    ]
    (
        response_message,
        used_agents,
        prev_messages,
        new_used_agents_count,
    ) = await service.process(
        request.user.wallet_id,
        request.chat_id,
        plugins,
        request.data.message,
        request.model,
    )

    def _get_structured_answer(answer) -> dict:
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
                "message": response_message["text_answer"],
                "structured_messages": [
                    json.dumps(_get_structured_answer(ans))
                    for ans in response_message["structured_answers"]
                ]
                if response_message["structured_answers"]
                else [],
                "message_id": request.data.message_id,
                "plugins_used": used_agents,
                "serialized_transaction": None,
            },
            "model": request.model,
            "aux": request.aux,
        }
    )

    await pub.publish("response_received", str(response))
    _send_literal_message(
        literal_client,
        request.chat_id,
        request.user.wallet_id,
        "user_message",
        f"User",
        request.data.message,
    )
    _send_literal_message(
        literal_client,
        request.chat_id,
        request.user.wallet_id,
        "assistant_message",
        f"Fridon",
        response_message["text_answer"] or response_message["structured_answers"],
    )
    await _handle_score(
        request,
        scorer_service,
        pub,
        used_agents,
        response_message,
        prev_messages,
        new_used_agents_count,
    )


@inject
async def user_message_handler(
    sub: redis.Subscription = Provide["subscription"],
    pub: redis.Publisher = Provide["publisher"],
    service: ProcessUserMessageService = Provide["process_user_message_service"],
    scorer_service: CalculateUserMessageScoreService = Provide[
        "calculate_user_message_score_service"
    ],
    literal_client=Provide["literal_client"],
):
    async for request in sub.channel("chat_message_created"):
        print(f"(Handler) Message Received: {request}")
        task = asyncio.create_task(
            task_runner(request, service, scorer_service, pub, literal_client)
        )


@inject
async def send_plugins(pub: redis.Publisher = Provide["publisher"]):
    registry = ensure_plugin_registry()
    plugins = [plugin_cls().to_json() for plugin_cls in registry.plugins.values()]

    plugins = [
        p for p in plugins if p["name"] not in ["off-topic", "Bonk Notifier", "Fridon"]
    ]

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
