from app.community.plugins.jupyter.utilities import JupyterSwapUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class JupyterSwapToopInput(BaseToolInput):
    from_token: str
    to_token: str
    amount: int | float


JupyterSwapTool = BaseTool(
    name="jupyter-swap",
    description="A utility that allows you to exchange one token to another using jupyter",
    args_schema=JupyterSwapToopInput,
    utility=JupyterSwapUtility(),
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

TOOLS = [JupyterSwapTool]
