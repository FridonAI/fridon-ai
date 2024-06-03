from app.community.plugins.symmetry.utilities import SymmetryBalanceUtility
from app.core.tools import BaseTool, BaseToolInput


class SymmetryBalanceToolInput(BaseToolInput):
    wallet_id: str


SymmetryBalanceTool = BaseTool(
    name="symmetry-balance",
    description="A utility that allows you to get balances from Symmetry",
    args_schema=SymmetryBalanceToolInput,
    utility=SymmetryBalanceUtility(),
)


TOOLS = [SymmetryBalanceTool]
