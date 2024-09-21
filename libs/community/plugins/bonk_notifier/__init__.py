from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry
from libs.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="bonk-bullish-notifier")
class BonkBullishNotifierPlugin(BasePlugin):
    name = "Bonk Bullish Notifier"
    description = "Get notification when BONK is bullish"
    owner = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    price = 1000
    tools: type[list[BaseTool]] = []
    exclude = True
    image_url = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/bonkheadog.png"
