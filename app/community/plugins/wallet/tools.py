from app.community.plugins.wallet.utilities import WalletBalanceUtility, WalletTransferUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class WalletBalanceToolInput(BaseToolInput):
    wallet_id: str


WalletBalanceTool = BaseTool(
    name="wallet-balance",
    description="A utility that allows you to get your wallet balances",
    args_schema=WalletBalanceToolInput,
    utility=WalletBalanceUtility(),
)


class WalletTransferToolInput(BaseToolInput):
    currency: str
    amount: int
    to_wallet_address: str


WalletTransferTool = BaseTool(
    name="wallet-transfer",
    description="A utility that allows you to transfer tokens to another wallet",
    args_schema=WalletTransferToolInput,
    utility=WalletTransferUtility(),
)


TOOLS = [WalletBalanceTool, WalletTransferTool]
