from libs.community.plugins.og_traders_simulator.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="og-traders-simulator")
class OGTradersSimulatorPlugin(BasePlugin):
    name: str = "OG Traders Simulator"
    description: str = (
        "AI agent simulating OG traders, for example EmperorBTC, or CryBull"
    )
    owner: str = "7fwBfKwFFmsXg2JjGPRhKSTPM3X5tVUYS59kHnVXKjXH"
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/emperor-plugin.jpg"
    json_format: bool = True
