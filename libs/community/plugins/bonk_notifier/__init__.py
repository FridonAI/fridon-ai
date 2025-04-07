from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool
plugin_registry = ensure_plugin_registry()

# @plugin_registry.register(name="bonk-notifier")
class BonkNotifierPlugin(BasePlugin):
    name: str = "Bonk Notifier"
    description: str = "AI agent for notifying users about state of the BONK token"
    tools: list[BaseTool] = []
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    exclude: bool = True
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/bonkheadog.png"
