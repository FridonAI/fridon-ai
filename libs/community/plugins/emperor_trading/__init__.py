from libs.community.plugins.emperor_trading.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register(name="emperor-trader")
class EmperorTradingPlugin(BasePlugin):
    name: str = "Emperor Trader"
    description: str = "AI plugin for trading based on BTC-Emperor's guide."
    owner: str = "7fwBfKwFFmsXg2JjGPRhKSTPM3X5tVUYS59kHnVXKjXH"
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/emperor-plugin.jpg"
    json_format: bool = True
