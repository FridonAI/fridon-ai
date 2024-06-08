from app.community.plugins.coin_technical_analyzer.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.plugins.registry import ensure_plugin_registry
from app.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register(name="coin-technical-analyzer")
class CoinsTechnicalAnalyzerPlugin(BasePlugin):
    name = "Coin Technical Analyzer"
    description = "Analyze coin price charts by indicators and analyse them."
    owner = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    price = 1000
    tools: type[list[BaseTool]] = TOOLS
