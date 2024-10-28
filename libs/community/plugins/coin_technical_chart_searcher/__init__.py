from libs.community.plugins.coin_technical_chart_searcher.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry
from fridonai_core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register(name="coin-technical-chart-searcher")
class CoinTechnicalChartSearcherPlugin(BasePlugin):
    name: str = "Coin Technical Chart Searcher"
    description: str = "AI plugin for searching coins by chart similarity with given coin or coin search by technical indicators."
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/chart-similarity-avatar.png"
    json_format: bool = True
