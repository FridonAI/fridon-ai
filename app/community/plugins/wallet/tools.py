from typing import Union

from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool
from app.settings import settings

if settings.ENV == 'mock':
    from app.community.plugins.wallet.mock.utilities import WalletBalanceMockUtility as WalletBalanceUtility, WalletTransferMockUtility as WalletTransferUtility
else:
    from app.community.plugins.wallet.utilities import WalletBalanceUtility, WalletTransferUtility

class WalletBalanceToolInput(BaseToolInput):
    currency: Union[str, None] = None


WalletBalanceTool = BaseTool(
    name="wallet-balance",
    description="A utility that allows you to get your coin balances on the wallet",
    args_schema=WalletBalanceToolInput,
    utility=WalletBalanceUtility(),
    examples=[
        {
            "request": "what's my balance",
            "response": "Currently you have 10 usdc and 10000000 bonk which is 288$ usd.",
        },
        {
            "request": "how much bonk I have?",
            "response": "You have 10000000 bonk with value 288$ usd.",
        },

        {
            "request": "how much sol I have?",
            "response": "You have 10 sol with value 1700$ usd.",
        },
    ]
)


class WalletTransferToolInput(BaseToolInput):
    currency: str
    amount: Union[float, int]
    to_wallet_address: str


WalletTransferTool = BaseTool(
    name="wallet-transfer",
    description="A utility that allows you to transfer tokens to another wallet",
    args_schema=WalletTransferToolInput,
    utility=WalletTransferUtility(),
    examples=[
        {
            "request": "transfer 10 usdc to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
            "response": "Transfer finished successfully!",
        },
        {
            "request": "transfer 10 bonk to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
            "response": "Transaction skipped, please try again.",
        }
    ]
)


TOOLS = [WalletBalanceTool, WalletTransferTool]
