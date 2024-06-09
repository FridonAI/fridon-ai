from app.community.plugins.wallet.utilities import WalletBalanceUtility, WalletTransferUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class WalletBalanceToolInput(BaseToolInput):
    currency: str | None = None


WalletBalanceTool = BaseTool(
    name="wallet-balance",
    description="A utility that allows you to get your coin balances on the wallet",
    args_schema=WalletBalanceToolInput,
    utility=WalletBalanceUtility(),
    examples=[
        "get my sol balance",
        "what's my balance",
        "how much bonk I have?"
    ]
)


class WalletTransferToolInput(BaseToolInput):
    currency: str
    amount: int | float
    to_wallet_address: str


WalletTransferTool = BaseTool(
    name="wallet-transfer",
    description="A utility that allows you to transfer tokens to another wallet",
    args_schema=WalletTransferToolInput,
    utility=WalletTransferUtility(),
    examples=[
        "please send 10 bonk to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
        "transfer 2 usdc to fridon.sol"
    ]
)


TOOLS = [WalletBalanceTool, WalletTransferTool]
