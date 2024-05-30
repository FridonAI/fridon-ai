from app.community.plugins.greeter.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.tools import BaseTool


class GreeterPlugin(BasePlugin):
    name = "greeter"
    description = "A simple plugin that greets the user"
    tools: type[list[BaseTool]] = TOOLS
