from libs.core.plugins.tools import BaseTool
from libs.community.plugins.wallet.tools import TOOLS
from libs.core.plugins import BasePlugin
from libs.core.plugins.registry import ensure_plugin_registry

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="wallet")
class WalletPlugin(BasePlugin):
    name: str = "Wallet"
    description: str = "Plugin with wallet related operations."
    tools: list[BaseTool] = TOOLS
