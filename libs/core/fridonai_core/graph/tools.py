from typing import List, Union

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
        __doc__="Transfer control to the assistant: "
        + plugin.full_description(tool_descriptions=False),
        request=(str, Field(description="Full requests from the user.")),
    )


class CompleteTool(BaseModel):
    """A tool to mark the current agent's work as completed with appropriate answer and return control to the main assistant,
    who can re-route the dialog based on the user's needs. Tool doesn't make up any information and is 100% precise with generating answer.
    If the agent's response was json object answer must be a dict otherwise it must be a string."""

    plugin_status: bool = Field(
        description="Plugin made it's job successfully, or not and something wrong happened"
    )
    answer: str = Field(
        description="Plugin's response, if json string is the response copy it as it is don't cut or add something."
    )
    is_json: bool = Field(description="If the answer is json string or not.")

    class Config:
        json_schema_extra = {
            "example": {
                "plugin_status": True,
                "answer": "Your sol balance is 20.",
            },
            "example 2": {
                "plugin_status": True,
                "answer": "You've successfully borrowed 10 sol on kamino",
            },
            "example 3": {"plugin_status": False, "answer": "Something went wrong!"},
            "example 4": {
                "plugin_status": False,
                "answer": {"data": {"sol": 12, "usdc": 10}},
            },
        }


class FinalResponse(BaseModel):
    """FinalResponse generator tool, in no other tools is going to be called this tool is called to generate the final answers.
    A tool to generate final response to the user's request. It must be the last tool call in the conversation with the final answer."""

    structured_answers: Union[List[Union[str, dict]], None] = Field(
        description="All json string answers from `CompletedTool`s should be copied here if they are json."
    )
    text_answer: Union[str, None] = Field(
        description="Union of tool text answers from `CompleteTool`s tools which wasn't they aren't json."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "structured_answers": [
                    '"data": {"sol": 12, "usdc": 10}}',
                    '"data": {"sol": 12, "usdc": 10}',
                ],
                "text_answer": "Your transaction successfully completed and you also successfully staked 10 sol on kamino.",
            },
            "example 2": {"text_answer": "Solana looks very decent to be bought."},
            "example 3": {
                "structured_answer": [
                    '"data": {"btc": {"score": 1',
                    '"eth": {"score": 0}}',
                ]
            },
        }
