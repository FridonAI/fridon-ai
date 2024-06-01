import os

os.environ["OPENAI_API_KEY"] = ""
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = "fridon"

os.environ["PLAYER_TEMPLATE_PATH"] = "./data/templates/"

from app.core.graph.workflows import graph

config = {
    "configurable": {
        "thread_id": "1",
        "wallet_id": "adasdasdad",
        "chat_id": "bla"
    }
}


for s in graph.stream(
    {
        "messages": [
            "are you all right?"
        ],
    },
    config,
    stream_mode="values"
):
    if "__end__" not in s:
        s["messages"][-1].pretty_print()
