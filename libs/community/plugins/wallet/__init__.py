from fridonai_core.plugins.tools import BaseTool
from libs.community.plugins.wallet.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="wallet")
class WalletPlugin(BasePlugin):
    name: str = "Wallet"
    description: str = "Plugin with wallet related operations."
    tools: list[BaseTool] = TOOLS
