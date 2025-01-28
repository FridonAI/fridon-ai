from fridonai_core.graph.base import generate_response
from fridonai_core.plugins.registry import ensure_plugin_registry


class ProcessUserMessageService:
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

        final_response, used_agents, prev_messages = await generate_response(
            message, plugins, config, memory="postgres"
        )

        return final_response, used_agents, prev_messages
