from dependency_injector.wiring import Provide, inject

from fridonai_core.graph.base import generate_response
from fridonai_core.plugins.registry import ensure_plugin_registry


class ProcessUserMessageService:
    @inject
    def __init__(self, literal_client=Provide["literal_client"]) -> None:
        self.literal_client = literal_client

    def _send_literal_message(
        self, thread_id, thread_name, message_type, message_name, message
    ):
        try:
            with self.literal_client.thread(
                thread_id=thread_id, name=thread_name
            ) as thread:
                self.literal_client.message(
                    content=message, type=message_type, name=message_name
                )
        except Exception as e:
            print(f"Error sending message to literal: {e}")

    async def _prepare_plugins(self, plugin_names):
        registry = ensure_plugin_registry()
        plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]
        plugins = [p for p in plugins if p.exclude is False]   
        return plugins
    

    async def process(
        self, wallet_id: str, chat_id: str, plugin_names: list[str], message: str
    ):
        plugins = await self._prepare_plugins(plugin_names)

        config = {
            "thread_id": chat_id,
            "wallet_id": wallet_id,
            "chat_id": chat_id,
        }

        final_response, used_agents = await generate_response(
            message,
            plugins,
            config,
            memory="postgres"
        )

        self._send_literal_message(
            chat_id, wallet_id, "user_message", f"User", message
        )
        self._send_literal_message(
            chat_id,
            wallet_id,
            "assistant_message",
            f"Fridon",
            final_response.text_answer
            or final_response.structured_answers,
        )

        return final_response, used_agents
