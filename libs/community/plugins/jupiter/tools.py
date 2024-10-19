from libs.community.adapters.redis_send_wait_adapter import BlockchainRedisSendWaitAdapter
from libs.community.plugins.jupiter.utilities import JupiterSwapUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool


class JupiterSwapToopInput(BaseToolInput):
    from_token: str
    to_token: str
    amount: float


JupiterSwapTool = BaseTool(
    name="jupiter-swap",
    description="A utility that allows you to exchange one token to another using jupiter",
    args_schema=JupiterSwapToopInput,
    utility=JupiterSwapUtility(communicator=BlockchainRedisSendWaitAdapter()),
    examples=[
        {
            "request": "Swap 10 sol to usdc",
            "response": "Swap finished successfully!",
        },
        {
            "request": "Swap 10 usdc to bonk",
            "response": "Transaction skipped, please try again.",
        },
    ],
)

TOOLS = [JupiterSwapTool]
