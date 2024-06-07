from app.community.plugins.wallet.tools import TOOLS
from app.core.plugins import BasePlugin
from app.core.plugins.registry import ensure_plugin_registry
from app.core.plugins.tools import BaseTool

plugin_registry = ensure_plugin_registry()

@plugin_registry.register(name="wallet")
class WalletPlugin(BasePlugin):
    name = "Wallet"
    description = "Plugin with wallet related operations."
    tools: type[list[BaseTool]] = TOOLS
