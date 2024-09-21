from libs.community.plugins.solana_bonk_educator.tools import TOOLS
from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry
from libs.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register("solana-bonk-educator")
class SolanaBonkEducatorPlugin(BasePlugin):
    name = "Solana Bonk Educator"
    description = "Bonk-Enriched Plugin, answers questions on crypto, blockchain operations, solana, bonk and more."
    owner = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: type[list[BaseTool]] = TOOLS
    image_url = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/solana-bonk-educator.png"
