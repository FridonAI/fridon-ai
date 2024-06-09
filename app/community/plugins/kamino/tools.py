from typing import Literal

from app.community.plugins.kamino.utilities import KaminoBorrowLendUtility, KaminoBalanceUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class KaminoBorrowLendToolInput(BaseToolInput):
    operation: Literal['borrow', 'lend', 'repay', 'withdraw']
    currency: str
    amount: int | float


KaminoBorrowLendTool = BaseTool(
    name="kamino-borrow-lend",
    description="A utility that allows you to borrow and lend tokens on Kamino",
    args_schema=KaminoBorrowLendToolInput,
    utility=KaminoBorrowLendUtility(),
    examples=[
        "borrow 10 usdc from kamino",
        "lend 10 sol to kamino",
        "repay 10 usdc from kamino",
        "withdraw 10 sol from kamino"
    ]
)


class KaminoBalanceToolInput(BaseToolInput):
    operation: str | None = None
    currency: str | None = None


KaminoBalanceTool = BaseTool(
    name="kamino-balance",
    description="A utility that allows you to get your Kamino balance",
    args_schema=KaminoBalanceToolInput,
    utility=KaminoBalanceUtility(),
    examples=["get my balances on kamino please", "how much sol is lend on kamino?"]
)

TOOLS = [KaminoBorrowLendTool, KaminoBalanceTool]
