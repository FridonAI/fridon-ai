import json

from dependency_injector.wiring import inject, Provide
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.graph import create_graph
from app.core.plugins.registry import ensure_plugin_registry

from app.settings import settings

class ProcessUserMessageService:
    @inject
    def __init__(
            self,
            literal_client=Provide["literal_client"]
    ) -> None:
        self.literal_client = literal_client

    def _send_literal_message(self, thread_id, thread_name, message_type, message_name, message):
        try:
            with self.literal_client.thread(thread_id=thread_id, name=thread_name) as thread:
                self.literal_client.message(content=message, type=message_type, name=message_name)
        except Exception as e:
            print(f"Error sending message to literal: {e}")

    async def _prepare_graph(self, plugin_names, memory):
        registry = ensure_plugin_registry()
        plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]
        plugins = [p for p in plugins if p.exclude is False]

        llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY, verbose=True)

        graph = create_graph(llm, plugins, memory=memory)
        return graph

    async def process(self, wallet_id: str, chat_id: str, plugin_names: list[str], message: str):
        async with AsyncPostgresSaver.from_conn_string(settings.POSTGRES_DB_URL, pipeline=False) as memory:
            await memory.setup()
            graph = await self._prepare_graph(plugin_names, memory)
            config = {
                "configurable": {
                    "thread_id": chat_id,
                    "wallet_id": wallet_id,
                    "chat_id": chat_id,
                }
            }
            response = ""
            async for s in graph.astream(
                {
                    "messages": [HumanMessage(content=message)],
                },
                config,
                stream_mode="values"
            ):
                if "__end__" not in s:
                    response = s["messages"][-1]
                    response.pretty_print()

            graph_state = await graph.aget_state(config)
            used_agents = list(set(graph_state.values.get("used_agents", [])))
            final_response = graph_state.values.get("final_response")
            self._send_literal_message(chat_id, wallet_id, "user_message", f"User", message)
            self._send_literal_message(chat_id, wallet_id, "assistant_message", f"Fridon", final_response.text_answer or json.dumps(final_response.structured_answers))

            return final_response, used_agents
