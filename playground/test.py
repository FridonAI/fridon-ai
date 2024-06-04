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

    plugin = registry.plugins["kamino"]()

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    graph = create_graph(llm, [plugin], memory=AsyncSqliteSaver.from_conn_string(":memory:"))

    config = {
        "configurable": {
            "thread_id": "1",
            "wallet_id": "adasdasdad",
            "chat_id": "bla"
        }
    }

    async for s in graph.astream(
            {
                "messages": [
                    "what's my balance?"
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