from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from fridonai_core.plugins.tools.base import BaseTool


def create_agent_chain(
    llm: BaseChatModel,
    prompt: ChatPromptTemplate,
    tools: list[BaseTool | type[BaseModel]],
    always_tool_call=False,
) -> Runnable:
    if always_tool_call:
        return prompt | llm.bind_tools(
            tools, tool_choice="any", parallel_tool_calls=False
        )
    return prompt | llm.bind_tools(tools, parallel_tool_calls=False)
