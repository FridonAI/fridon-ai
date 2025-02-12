from fridonai_core.plugins.tools import BaseTool
from libs.community.plugins.wallet.tools import TOOLS
from fridonai_core.plugins import BasePlugin
from fridonai_core.plugins.registry import ensure_plugin_registry

plugin_registry = ensure_plugin_registry()


@plugin_registry.register(name="wallet")
class WalletPlugin(BasePlugin):
    name: str = "Wallet"
    description: str = "Blockchain related operations: transfer, swap, get balances. Unifying different protocols."
    owner: str = "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"
    tools: list[BaseTool] = TOOLS
    image_url: str = "https://fridon-ai-assets.s3.eu-central-1.amazonaws.com/agent-avatars/wallet-avatar.png"
