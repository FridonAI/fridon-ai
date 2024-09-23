from libs.community.plugins.jupiter.tools import TOOLS
from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry
from libs.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="jupiter")
class JupiterPlugin(BasePlugin):
    name: str = "Jupiter"
    description: str = "Swap one coin to another with this Plugin."
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
