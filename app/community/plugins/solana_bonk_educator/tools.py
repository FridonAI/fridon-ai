from app.community.plugins.solana_bonk_educator.utilities import SolanaBonkUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool

class SolanaEducatorInput(BaseToolInput):
    request: str


SolanaEducatorTool = BaseTool(
    name="solana-educator",
    description="Use this tool to answer questions about solana, crypto, protocols, and more. Always use this tool.",
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
        }
    ]
)


TOOLS = [SolanaEducatorTool]
