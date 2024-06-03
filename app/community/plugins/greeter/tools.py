from app.community.plugins.greeter.utilities import HelloUtility
from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.tools import BaseTool


class HelloToolInput(BaseToolInput):
    name: str


HelloTool = BaseTool(
    name = "hello",
    description = "A simple tool that greets the user",
    args_schema = HelloToolInput,
    utility = HelloUtility(),
)


TOOLS = [HelloTool]
