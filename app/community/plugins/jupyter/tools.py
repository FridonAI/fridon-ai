from app.community.plugins.jupyter.utilities import JupyterSwapUtility
from app.core.tools import BaseToolInput, BaseTool


class JupyterSwapToopInput(BaseToolInput):
    from_token: str
    to_token: str
    amount: int


JupyterSwapTool = BaseTool(
    name="jupyter-swap",
    description="A utility that allows you to exchange one token to another using jupyter",
    args_schema=JupyterSwapToopInput,
    utility=JupyterSwapUtility(),
)

TOOLS = [JupyterSwapTool]
