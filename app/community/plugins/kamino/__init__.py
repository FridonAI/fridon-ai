from app.community.plugins.kamino.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.tools import BaseTool


class KaminoPlugin(BasePlugin):
    name = "kamino-borrow-lend"
    description = "Kamino plugin that allows you to borrow and lend tokens on Kamino"
    tools: type[list[BaseTool]] = TOOLS
