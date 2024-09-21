from libs.community.plugins.fridon.utilities import FridonRagUtility
from libs.core.plugins.schemas import BaseToolInput
from libs.core.plugins.tools import BaseTool


class FridonRagInput(BaseToolInput):
    question: str


FridonRagTool = BaseTool(
    name="fridon-rag",
    description="Use this tool to answer questions about FridonAI",
    args_schema=FridonRagInput,
    utility=FridonRagUtility(),
    examples=[
        {
            "request": "Who are you?",
            "response": "",
        },
        {
            "request": "What plugins do you have?",
            "response": "",
        },
    ],
)


TOOLS = [FridonRagTool]
