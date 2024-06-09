from app.community.plugins.fridon.utilities import FridonRagUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class FridonRagInput(BaseToolInput):
    question: str


FridonRagTool = BaseTool(
    name="fridon-rag",
    description="Use this tool to answer questions about FridonAI",
    args_schema=FridonRagInput,
    utility=FridonRagUtility(),
)


TOOLS = [FridonRagTool]
