from libs.community.plugins.fridon.tools import TOOLS
from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry
from libs.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register("fridon")
class FridonPlugin(BasePlugin):
    name: str = "Fridon"
    description: str = "Plugin for getting information about FridonAI"
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
