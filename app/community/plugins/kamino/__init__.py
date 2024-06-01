from app.community.plugins.kamino.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.registry import ensure_plugin_registry
from app.core.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register
class KaminoPlugin(BasePlugin):
    name = "kamino"
    description = "Kamino Plugin"
    tools: type[list[BaseTool]] = TOOLS
