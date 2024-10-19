from libs.community.plugins.coin_technical_analyzer.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="coin-technical-analyzer")
class CoinsTechnicalAnalyzerPlugin(BasePlugin):
    name: str = "Coin Technical Analyzer"
    description: str = "AI plugin for analyzing and plotting coin price charts with technical indicators."
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/coin-ta.png"
    json_format: bool = True
