from app.community.plugins.greeter.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.registry import ensure_plugin_registry
from app.core.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register
class GreeterPlugin(BasePlugin):
    name = "greeter"
    description = "A simple plugin that greets the user"
    tools: type[list[BaseTool]] = TOOLS
