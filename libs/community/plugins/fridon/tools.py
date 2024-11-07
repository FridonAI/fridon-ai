from libs.community.plugins.fridon.utilities import FridonRagUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool


class FridonResponderInput(BaseToolInput):
    question: str


FridonResponderTool = BaseTool(
    name="fridon-responder",
    description="Always use this tool to answer questions before CompleteTool.",
    args_schema=FridonResponderInput,
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
        {
            "request": "What do you do?",
            "response": "",
        },
        {
            "request": "What is FridonAI's features?",
            "response": "",
        },
    ],
)


TOOLS = [FridonResponderTool]
