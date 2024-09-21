from typing import Union

from langchain_core.pydantic_v1 import BaseModel, Field


class ResponseSchema(BaseModel):
    plugin_status: bool = Field(
        description="Plugin made it's job successfully, or not and something wrong happened"
    )
    answer_text: str = Field(description="Text response from the plugin")
    structured_response: Union[dict, BaseModel] = Field(
        description="Structured response from the plugin"
    )
