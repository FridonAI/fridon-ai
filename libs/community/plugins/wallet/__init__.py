from fridonai_core.plugins.tools import BaseTool
from libs.community.plugins.wallet.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="wallet")
class WalletPlugin(BasePlugin):
    name: str = "Wallet"
    description: str = "Plugin with wallet related operations, get balances, send tokens, etc."
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/wallet-avatar.png"
