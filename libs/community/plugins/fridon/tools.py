from libs.community.plugins.fridon.utilities import FridonRagUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from pydantic import Field


class FridonResponderInput(BaseToolInput):
    question: str = Field(..., description="The question about FridonAI")


FridonResponderTool = BaseTool(
    name="fridon-responder",
    description="Always use this tool to answer questions before CompleteTool.",
    args_schema=FridonResponderInput,
    utility=FridonRagUtility(),
    examples=[
        {
            "request": "What are you?",
            "response": "",
        },
        {
            "request": "What plugins do you have?",
            "response": "",
        },
        {
            "request": "Tell me about yourself",
            "response": "",
        },
        {
            "request": "What is FridonAI's features?",
            "response": "",
        },
        {
            "request": "How can I use coin searcher plugin?",
            "response": "",
        },
    ],
)


TOOLS = [FridonResponderTool]
