from typing import Union

from pydantic import BaseModel, Field, create_model, ConfigDict

from fridonai_core.plugins import BasePlugin

def create_plugin_wrapper_tool(plugin: BasePlugin, class_name: str) -> type[BaseModel]:
    return create_model(
        f"To{class_name}",
        __config__=type(
            "Config",
            (ConfigDict,),
            {
                "json_schema_extra": {
                    "Example#" + str(i + 1): {"request": example}
                    for i, example in enumerate(plugin.request_examples)
                }
            },
        ),
        __doc__=plugin.full_description(tool_descriptions=False),
        request=(str, Field(description="Full requests from the user.")),
    )


class CompleteTool(BaseModel):
    text_answer: str = Field(description="Agent's final answer to the user's request.")
    structured_answers: list[dict] = Field(
        description="Structured answers from the agent."
    )
