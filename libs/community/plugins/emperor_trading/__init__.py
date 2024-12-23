from libs.community.plugins.emperor_trading.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register(name="emperor-trading")
class EmperorTradingPlugin(BasePlugin):
    name: str = "Emperor Trading"
    description: str = "AI plugin for trading based on BTC-Emperor guide."
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/emperor-plugin.jpg"
    json_format: bool = True
