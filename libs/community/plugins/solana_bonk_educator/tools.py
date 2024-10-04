from libs.community.plugins.solana_bonk_educator.utilities import SolanaBonkUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool


class SolanaEducatorInput(BaseToolInput):
    request: str


SolanaEducatorTool = BaseTool(
    name="solana-educator",
    description="Always use this tool for answering questions about solana, crypto, blockchain protocols, bonk and so on.",
    args_schema=SolanaEducatorInput,
    utility=SolanaBonkUtility(),
    examples=[
        {
            "request": "What's staking?",
            "response": "",
        },
        {
            "request": "What's solana?",
            "response": "",
        },
        {
            "request": "How can I swap coins on solana?",
            "response": "",
        },
    ],
)


TOOLS = [SolanaEducatorTool]
