from app.community.plugins.symmetry.utilities import SymmetryBalanceUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class SymmetryBalanceToolInput(BaseToolInput):
    pass


SymmetryBalanceTool = BaseTool(
    name="symmetry-balance",
    description="A utility that allows you to get balances from Symmetry",
    args_schema=SymmetryBalanceToolInput,
    utility=SymmetryBalanceUtility(),
    examples=[
        "Can you show me my balances on Symmetry?",
        "Show me my basket balances on symmetry please.",
    ]
)


TOOLS = [SymmetryBalanceTool]
