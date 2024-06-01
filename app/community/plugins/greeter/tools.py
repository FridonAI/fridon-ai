from app.community.plugins.greeter.utilities import HelloUtility
from app.core.tools import BaseTool, BaseToolInput


class HelloToolInput(BaseToolInput):
    name: str


HelloTool = BaseTool(
    name = "hello",
    description = "A simple tool that greets the user",
    args_schema = HelloToolInput,
    utility = HelloUtility(),
)


TOOLS = [HelloTool]
