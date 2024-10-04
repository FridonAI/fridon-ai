import json
from typing import Any
import uuid

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
    dump_json_data: bool = False

    def _run(
        self,
        *args,
        config: RunnableConfig | None = None,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs,
    ) -> str | Any:
        config_ = config.get("configurable", {})
        result = self.utility.run(
            *args,
            **{**kwargs, **config_},
        )
        if self.dump_json_data and isinstance(result, dict):
            result = self._dump_to_tmp(result)
        elif isinstance(result, dict):
            result = json.dumps(result)
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
        if self.dump_json_data and isinstance(result, dict):
            result = self._dump_to_tmp(result)
        return result
    

    def _dump_to_tmp(self, result: str | Any):
        temp_file_id = str(uuid.uuid4())[:8]
        try:
            with open(f"tmp/{temp_file_id}.json", 'w') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return result

        return json.dumps({
            "type": "fileObject",
            "name": self.name,
            "tmp_file_id": temp_file_id,
            "path": f"tmp/{temp_file_id}.json",
        })
        

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
