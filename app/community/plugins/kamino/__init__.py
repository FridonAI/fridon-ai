from app.community.plugins.kamino.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.tools import BaseTool


class KaminoPlugin(BasePlugin):
    name = "kamino"
    description = "Kamino Plugin"
    tools: type[list[BaseTool]] = TOOLS
