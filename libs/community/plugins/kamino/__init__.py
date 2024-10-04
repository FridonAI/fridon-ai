from libs.community.plugins.kamino.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="kamino")
class KaminoPlugin(BasePlugin):
    name: str = "Kamino"
    description: str = "Plugin supporting Kamino operations: lend, borrow, repay, withdraw."
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
