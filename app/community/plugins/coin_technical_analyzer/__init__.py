from app.community.plugins.coin_technical_analyzer.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.plugins.registry import ensure_plugin_registry
from app.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register(name="coins_technical_analyzer")
class CoinsTechnicalAnalyzerPlugin(BasePlugin):
    name = "coins_technical_analyzer"
    description = "Analyze coin price charts by indicators and analyse them."
    tools: type[list[BaseTool]] = TOOLS
