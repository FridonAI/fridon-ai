from libs.community.plugins.kamino.tools import TOOLS
from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry
from libs.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="kamino")
class KaminoPlugin(BasePlugin):
    name = "Kamino"
    description = "Plugin supporting Kamino operations: lend, borrow, repay, withdraw."
    owner = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: type[list[BaseTool]] = TOOLS