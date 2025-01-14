from libs.community.plugins.fridon.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register("off-topic")
class OffTopicPlugin(BasePlugin):
    name: str = "off-topic"
    description: str = "Agent for responding to off-topic requests, which are not related to FridonAI plugins."
    tools: list[BaseTool] = TOOLS
