from pydantic.v1 import BaseModel

from app.core.plugins.tools import BaseTool


class BasePlugin(BaseModel):
    name: str
    description: str
    tools: type[list[BaseTool]]
