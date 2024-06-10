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
        {
            "request": "get my balances on symmetry please",
            "response": "",
        },

        {
            "request": "how much sol is supplied on symmetry?",
            "response": "",
        },
    ]
)


TOOLS = [SymmetryBalanceTool]
