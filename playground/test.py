from langchain_openai.chat_models import ChatOpenAI
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

import os

os.environ["OPENAI_API_KEY"] = ""
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = "fridon"

os.environ["PLAYER_TEMPLATE_PATH"] = "./data/templates/"

from app.core.graph import create_graph
from app.core.plugins.registry import ensure_plugin_registry

async def main():
    registry = ensure_plugin_registry()
    print(registry.plugins)

    plugin_names = ["greeter", "kamino", "wallet", "jupiter", "symmetry", "coin-price-chart-similarity-search",
                    "coin-technical-analyzer"]
    registry = ensure_plugin_registry()

    plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]

    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY, verbose=True)

    graph = create_graph(llm, plugins, memory=AsyncSqliteSaver.from_conn_string(":memory:"))

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
                    "transfer 10 sol please",
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
