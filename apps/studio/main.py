from fridonai_core.graph.models import get_model
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver

from fridonai_core.graph import create_graph
from fridonai_core.plugins.registry import ensure_plugin_registry
from settings import settings
from apps.fridon_brain import _preload_modules


def test_chat():
    _preload_modules()
    plugin_names = [
        "wallet",
        "fridon",
        "coin-technical-analyzer",
        "coin-price-chart-similarity-search",
    ]
    registry = ensure_plugin_registry()
    plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]
    plugins = [p for p in plugins if p.exclude is False]

    llm = get_model()

    with SqliteSaver.from_conn_string(":memory:") as saver:
        graph = create_graph(llm, plugins, memory=saver)

    return graph
