from typing import Union

from pydantic.v1 import BaseConfig, BaseModel, Field, create_model

from app.core.plugins import BasePlugin


def create_plugin_wrapper_tool(plugin: BasePlugin, class_name: str) -> type[BaseModel]:
    return create_model(
        f"To{class_name}",
        __config__=type("Config", (BaseConfig,), {"schema_extra": {"Example#"+str(i+1): {"request": example }for i, example in enumerate(plugin.request_examples)}}),
        __doc__="Transfer control to the assistant: " + plugin.full_description(),
        request=(str, Field(description="Full requests from the user."))
    )

class CompleteTool(BaseModel):
    """A tool to mark the current agent's work as completed with appropriate answer and return control to the main assistant,
    who can re-route the dialog based on the user's needs. Tool doesn't make up any information and is 100% precise with generating answer.
    If the agent's response was json object answer must be a dict otherwise it must be a string."""
    plugin_status: bool = Field(description="Plugin made it's job successfully, or not and something wrong happened")
    answer: Union[dict, str] = Field(description="Plugin's response, it dictionary if json object is agent's response, otherwise string.")

    class Config:
        schema_extra = {
            "example": {
                "plugin_status": True,
                "answer": "Your sol balance is 20.",
            },
            "example 2": {
                "plugin_status": True,
                "answer": "You've successfully borrowed 10 sol on kamino",
            },
            "example 3": {
                "plugin_status": False,
                "answer": "Something went wrong!"
            },
            "example 4": {
                "plugin_status": False,
                "answer": {"data": {"sol": 12, "usdc": 10}}
            }
        }