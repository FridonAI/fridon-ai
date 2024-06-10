from app.community.plugins.solana_bonk_educator.utilities import SolanaBonkUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool

class SolanaEducatorInput(BaseToolInput):
    request: str


SolanaEducatorTool = BaseTool(
    name="solana-educator",
    description="Use this tool to answer questions about solana, crypto, protocols, and more.",
    args_schema=SolanaEducatorInput,
    utility=SolanaBonkUtility(),
    examples=[
        "What's staking?",
        "What's solana?",
        "How can I swap coins on solana?",
    ]
)


TOOLS = [SolanaEducatorTool]
