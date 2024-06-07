from dependency_injector.wiring import inject, Provide
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

from app.core.graph import create_graph
from app.core.plugins.registry import ensure_plugin_registry

from app.settings import settings

from app.core.checkpoint import PostgresSaver
from psycopg_pool import AsyncConnectionPool


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

    @staticmethod
    async def _prepare_memory() -> BaseCheckpointSaver:
        pool = AsyncConnectionPool(
            conninfo=settings.POSTGRES_DB_URL,
            max_size=20,
        )

        await PostgresSaver.acreate_tables(pool)

        return PostgresSaver(async_connection=pool)

    async def _prepare_graph(self, plugin_names):
        registry = ensure_plugin_registry()
        plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]

        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY, verbose=True)

        memory = await self._prepare_memory()

        graph = create_graph(llm, plugins, memory=AsyncSqliteSaver.from_conn_string(":memory:"))
        return graph

    async def process(self, wallet_id: str, chat_id: str, plugin_names: list[str], message: str):
        graph = await self._prepare_graph(plugin_names)
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
        used_agents = (await graph.aget_state(config)).values.get("used_agents", [])
        self._send_literal_message(chat_id, wallet_id, "user_message", f"User", message)
        self._send_literal_message(chat_id, wallet_id, "assistant_message", f"Fridon", response.content)
        return response.content, used_agents
