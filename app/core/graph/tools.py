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
    who can re-route the dialog based on the user's needs. It collects all tool call results and returns them as a single answer."""
    answer: str

    class Config:
        schema_extra = {
            "example": {
                "answer": "Your sol balance is 20.",
            },
            "example 2": {
                "answer": "You've successfully borrowed 10 sol on kamino",
            },
        }