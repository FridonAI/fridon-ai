from app.community.plugins.jupiter.utilities import JupiterSwapUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class JupiterSwapToopInput(BaseToolInput):
    from_token: str
    to_token: str
    amount: float


JupiterSwapTool = BaseTool(
    name="jupiter-swap",
    description="A utility that allows you to exchange one token to another using jupiter",
    args_schema=JupiterSwapToopInput,
    utility=JupiterSwapUtility(),
    examples=[
        {
            "request": "swap 10 sol to usdc",
            "response": "Swap finished successfully!",
        },
        {
            "request": "swap 10 usdc to bonk",
            "response": "Transaction skipped, please try again.",
        }
    ],
)

TOOLS = [JupiterSwapTool]
