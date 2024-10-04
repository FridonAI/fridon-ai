from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="bonk-bullish-notifier")
class BonkBullishNotifierPlugin(BasePlugin):
    name: str = "Bonk Bullish Notifier"
    description: str = "Get notification when BONK is bullish"
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    price: int = 1000
    tools: list[BaseTool] = []
    exclude: bool = True
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/bonkheadog.png"
