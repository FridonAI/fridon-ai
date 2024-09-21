from libs.community.plugins.coin_technical_analyzer.tools import TOOLS
from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry
from libs.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="coin-technical-analyzer")
class CoinsTechnicalAnalyzerPlugin(BasePlugin):
    name = "Coin Technical Analyzer"
    description = "AI plugin for analyze coin price charts by indicators, search coins by indicators."
    owner = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: type[list[BaseTool]] = TOOLS
    image_url = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/coin-ta.png"
