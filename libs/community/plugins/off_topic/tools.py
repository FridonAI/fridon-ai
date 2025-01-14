from libs.community.plugins.off_topic.utilities import OffTopicUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool
from pydantic import Field


class OffTopicToolInput(BaseToolInput):
    request: str = Field(..., description="The off-topic request")


OffTopicTool = BaseTool(
    name="off-topic",
    description="Off topic questions, not related to FridonAI plugins.",
    args_schema=OffTopicToolInput,
    utility=OffTopicUtility(),
    examples=[
        {
            "request": "Who is lebron james?",
            "response": "",
        },
        {
            "request": "How important marketing is in crypto?",
            "response": "",
        },
        {
            "request": "What's difference between IDO and ICO?",
            "response": "",
        },
    ],
)


TOOLS = [OffTopicTool]
