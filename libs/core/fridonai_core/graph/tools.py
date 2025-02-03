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
    """Finalizes the agent's execution by providing a precise, complete answer.

    IMPORTANT: Before using this tool, carefully analyze the previous tool's output:
    1. Check if the previous response exists and what format it's in (JSON or plain text)
    2. Determine if the execution was successful
    3. Do not modify or infer any values - use exactly what was provided

    This tool is used to indicate that the current work is complete and returns the final answer with no alterations or additional content.
    The answer must meet the following criteria:

    - If the previous tool's output is a JSON or a JSON string, then the answer must be provided as an unmodified JSON string.
    - Otherwise, the answer must be presented as plain text.

    Do not use this tool if there is no previous tool output to process.
    """

    plugin_status: bool = Field(
        description="Indicates whether the plugin completed its task successfully (True) or encountered an error (False). Must be based on the actual previous tool execution status."
    )
    answer: str = Field(
        description="The plugin's final response. Must be copied exactly from the previous tool's output - provide the exact JSON string if the answer is in JSON format, or the plain text string otherwise. Do not modify or infer values."
    )
    is_json: bool = Field(
        description="A flag that must be True if and only if the answer is a valid JSON string, and False if it is plain text. This should be determined by examining the actual previous tool output."
    )

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


class FinalTextResponse(BaseModel):
    """Defines the final text response for fulfilling a user's request.
    This model consolidates outputs from all tool text responses with name 'RESULT'.
    Fields:
      - text_answer: A single text response aggregating outputs.
    """

    text_answer: Union[str, None] = Field(
        description="The consolidated response from all tool text responses with name 'RESULT'."
    )

    class Config:
        json_schema_extra = {
            "example 1": {
                "text_answer": "Your transaction successfully completed and you also successfully staked 10 sol on kamino.",
            },
            "example 2": {"text_answer": ""},
        }
