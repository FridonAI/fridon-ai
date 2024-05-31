from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_core.tools import BaseTool as LangchainBaseTool
from pydantic.v1 import BaseModel

from app.core.utilities import BaseUtility
from langchain_core.runnables import ensure_config


class BaseToolInput(BaseModel):
    pass


class BaseTool(LangchainBaseTool):
    name: str
    description: str
    args_schema: type[BaseToolInput] | None = None
    utility: BaseUtility

    def _run(self, *args, run_manager: CallbackManagerForToolRun | None = None, **kwargs) -> str:
        return self.utility.run(
        *args,
            config=ensure_config().get("configurable", {}),
            **kwargs,
        )
