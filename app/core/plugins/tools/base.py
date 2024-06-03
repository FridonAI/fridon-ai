from typing import Any

from langchain.callbacks.manager import AsyncCallbackManager, CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool as LangchainBaseTool

from app.core.plugins.schemas import BaseToolInput
from app.core.utilities import BaseUtility


class BaseTool(LangchainBaseTool):
    name: str
    description: str
    args_schema: type[BaseToolInput] | None = None
    utility: BaseUtility

    def _run(
        self,
        *args,
        config: RunnableConfig | None = None,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> str | Any:
        config_ = config.get("configurable", {})
        return self.utility.run(
            *args,
            **{**kwargs, **config_},
        )

    def _arun(
        self,
        *args,
        config: RunnableConfig | None = None,
        run_manager: AsyncCallbackManager | None = None,
        **kwargs,
    ) -> str | Any:
        config_ = config.get("configurable", {})
        return self.utility.arun(
            *args,
            **{**kwargs, **config_},
        )
