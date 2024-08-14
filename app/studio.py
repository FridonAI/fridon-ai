from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from app import _preload_modules

from app.core.graph import create_graph
from app.core.plugins.registry import ensure_plugin_registry
from app.settings import settings

def _prepare_graph(plugin_names):
    registry = ensure_plugin_registry()
    plugins = [registry.plugins[plugin_name]() for plugin_name in plugin_names]
    plugins = [p for p in plugins if p.exclude is False]

    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY, verbose=True)
    with SqliteSaver.from_conn_string(":memory:") as saver:
        graph = create_graph(llm, plugins, memory=saver)
    return graph
def test_chat():
    _preload_modules()

    plugin_names = ["wallet", "fridon", "coin-technical-analyzer", "coin-price-chart-similarity-search", "jupiter"]
    graph = _prepare_graph(plugin_names)

    return graph

