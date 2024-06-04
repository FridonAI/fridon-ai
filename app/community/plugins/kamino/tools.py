from app.community.plugins.kamino.utilities import KaminoBorrowLendUtility, KaminoBalanceUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class KaminoBorrowLendToolInput(BaseToolInput):
    operation: str
    currency: str
    amount: int


KaminoBorrowLendTool = BaseTool(
    name="kamino-borrow-lend",
    description="A utility that allows you to borrow and lend tokens on Kamino",
    args_schema=KaminoBorrowLendToolInput,
    utility=KaminoBorrowLendUtility(),
)


class KaminoBalanceToolInput(BaseToolInput):
    pass


KaminoBalanceTool = BaseTool(
    name="kamino-balance",
    description="A utility that allows you to get your Kamino balance",
    args_schema=KaminoBalanceToolInput,
    utility=KaminoBalanceUtility(),
)

TOOLS = [KaminoBorrowLendTool, KaminoBalanceTool]
