from apps.studio.settings import settings
from fridonai_core.graph.models import get_model
from langgraph.checkpoint.sqlite import SqliteSaver

from fridonai_core.graph import create_graph
from fridonai_core.plugins.registry import ensure_plugin_registry
from apps.fridon_brain import _preload_modules


def test_chat():
    _preload_modules()

    plugin_names = [
        "coin-technical-chart-searcher",
        "coin-technical-analyzer",
        "coin-observer",
        "wallet",
        "jupiter",
        "fridon",
        "solana-bonk-educator",
        "emperor-trading",
        "off-topic",
    ]
    registry = ensure_plugin_registry()
    plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]
    plugins = [p for p in plugins if p.exclude is False]

    llm = get_model()

    with SqliteSaver.from_conn_string(":memory:") as saver:
        graph = create_graph(llm, plugins, memory=saver)

    return graph
