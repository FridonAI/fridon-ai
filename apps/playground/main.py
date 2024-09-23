from langchain_openai.chat_models import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from libs.core.graph import create_graph
from libs.core.plugins.registry import ensure_plugin_registry
from apps.fridon_brain import _preload_modules

from settings import settings

async def main():
    _preload_modules()
    plugin_names = ["wallet", "fridon", "coin-price-chart-similarity-search", "coin-technical-analyzer"]
    registry = ensure_plugin_registry()

    plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]

    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY, verbose=True)

    async with AsyncPostgresSaver.from_conn_string(settings.POSTGRES_DB_URL, pipeline=False) as saver:
        print(saver)
        await saver.setup()
        graph = create_graph(llm, plugins, memory=saver)
        print(graph.checkpointer)
        config = {  
            "configurable": {
                "thread_id": "1",
                "wallet_id": "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
                "chat_id": "bla"
            }
        }

        async for s in graph.astream(
                {
                    "messages": [
                        "who are you?",
                    ],
                },
                config,
                stream_mode="values"
        ):
            if "__end__" not in s:
                s["messages"][-1].pretty_print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
