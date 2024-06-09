from typing import Literal

from app.community.plugins.kamino.utilities import KaminoBorrowLendUtility, KaminoBalanceUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class KaminoBorrowLendToolInput(BaseToolInput):
    operation: Literal['borrow', 'supply', 'repay', 'withdraw']
    currency: str
    amount: int | float


KaminoBorrowLendTool = BaseTool(
    name="kamino-borrow-lend",
    description="Only use that tool for Kamino operations such as borrow, supply, repay and withdraw coins on Kamino",
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
    operation: Literal['borrow', 'supply', 'repay', 'withdraw'] | None = None
    currency: str | None = None


KaminoBalanceTool = BaseTool(
    name="kamino-balance",
    description="Only use that tool to get your Kamino balances, how much you've supplied or borrowed specific coins",
    args_schema=KaminoBalanceToolInput,
    utility=KaminoBalanceUtility(),
    examples=["get my balances on kamino please", "how much sol is supplied on kamino?"]
)

TOOLS = [KaminoBorrowLendTool, KaminoBalanceTool]
