from libs.community.plugins.coin_price_chart_similarity_search.tools import TOOLS
from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry
from libs.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register(name="coin-price-chart-similarity-search")
class CoinPriceChartSimilaritySearchPlugin(BasePlugin):
    name: str = "Coin Price Chart Similarity Search"
    description: str = "AI plugin for search coins similar to a given coin by price chart similarity."
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    price: float | int = 1000
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/chart-similarity-avatar.png"
    json_format: bool = True
