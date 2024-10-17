import json
from typing import Any
import uuid

from fridonai_core.plugins.tools.response_dumper_base import ResponseDumper
from langchain.callbacks.manager import AsyncCallbackManager, CallbackManagerForToolRun
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.tools import BaseTool as LangchainBaseTool

from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.utilities import BaseUtility


class BaseTool(LangchainBaseTool):
    name: str
    description: str
    args_schema: type[BaseToolInput] | None = None
    utility: BaseUtility
    examples: list[dict] = []
    helper: bool = False
    response_dumper: ResponseDumper | None = None

    def _run(
        self,
        *args,
        config: RunnableConfig | None = None,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> dict | str | Any:
        config_ = config.get("configurable", {})
        result = self.utility.run(
            *args,
            **{**kwargs, **config_},
        )
        if self.response_dumper and (isinstance(result, dict) or isinstance(result, list)):
            import asyncio
            return (asyncio.run(self.response_dumper.dump(result, self.name))).dict()
        return result

    async def _arun(
        self,
        *args,
        config: RunnableConfig | None = None,
        run_manager: AsyncCallbackManager | None = None,
        **kwargs,
    ) -> str | Any:
        config = ensure_config()
        config_ = config.get("configurable", {})
        result = await self.utility.arun(
            *args,
            **{**kwargs, **config_},
        )
        if self.response_dumper and (isinstance(result, dict) or isinstance(result, list)):
            return (await self.response_dumper.dump(result, self.name)).dict()
        return result
    
    @property
    def parameters_as_str(self):
        return self.args_schema.class_parameters_as_string()

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "examples": self.examples,
            "parameters": self.parameters_as_str,
        }
