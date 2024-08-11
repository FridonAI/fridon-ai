from typing import Literal, Union

from app.community.plugins.kamino.utilities import KaminoBorrowLendUtility, KaminoBalanceUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class KaminoBorrowLendToolInput(BaseToolInput):
    operation: Literal['borrow', 'supply', 'repay', 'withdraw']
    currency: str
    amount: Union[float, int]


KaminoBorrowLendTool = BaseTool(
    name="kamino-borrow-lend",
    description="Only use that tool for Kamino operations such as borrow, supply, repay and withdraw coins on Kamino",
    args_schema=KaminoBorrowLendToolInput,
    utility=KaminoBorrowLendUtility(),
    examples=[
        {
            "request": "borrow 10 sol from kamino",
            "response": "You borrowed 10 sol successfully!",
        },
        {
            "request": "supply 10 usdc to kamino",
            "response": "Lending transaction skipped, please try again.",
        },
        {
            "request": "repay 10 usdc from kamino",
            "response": "Repay finished successfully!",
        },
        {
            "request": "withdraw 10 sol from kamino",
            "response": "Withdraw finished successfully!",
        }
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
    examples=[
        {
            "request": "get my balances on kamino please",
            "response": "Currently you have 10 usdc borrowed and 10 sol supplied.",
        },
        {
            "request": "how much sol is supplied on kamino?",
            "response": "You currently have 10 sol supplied.",
        },
    ]
)

TOOLS = [KaminoBorrowLendTool, KaminoBalanceTool]
