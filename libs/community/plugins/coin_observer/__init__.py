from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

from libs.community.plugins.coin_observer.tools import TOOLS

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="coin-observer")
class CoinObserverPlugin(BasePlugin):
    name: str = "Coin Observer"
    description: str = (
        "Plugin for monitoring coin prices and sending notifications based on user conditions."
    )
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/coin-observer-avatar.png"
    json_format: bool = False
