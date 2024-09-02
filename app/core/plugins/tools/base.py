from typing import Any

from langchain.callbacks.manager import AsyncCallbackManager, CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.tools import BaseTool as LangchainBaseTool

from app.core.plugins.schemas import BaseToolInput
from app.core.plugins.utilities import BaseUtility


class BaseTool(LangchainBaseTool):
    name: str
    description: str
    args_schema: type[BaseToolInput] | None = None
    utility: BaseUtility
    examples: list[dict] = []
    helper: bool = False

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

    async def _arun(
        self,
        *args,
        config: RunnableConfig | None = None,
        run_manager: AsyncCallbackManager | None = None,
        **kwargs,
    ) -> str | Any:
        config = ensure_config()
        config_ = config.get("configurable", {})
        return await self.utility.arun(
            *args,
            **{**kwargs, **config_},
        )

    @property
    def parameters_as_str(self):
        return self.args_schema.class_parameters_as_string()

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "examples": self.examples,
            "parameters": self.parameters_as_str
        }