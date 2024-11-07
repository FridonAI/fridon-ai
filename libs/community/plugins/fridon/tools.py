from libs.community.plugins.fridon.utilities import FridonRagUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool


class FridonRagInput(BaseToolInput):
    question: str


FridonRagTool = BaseTool(
    name="ask-anything-about-fridon",
    description="Always use this tool to answer questions about you, don't answer yourself, always call this tool.",
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


TOOLS = [FridonRagTool]
