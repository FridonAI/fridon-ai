from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from app.core.plugins.tools.base import BaseTool


def create_agent_chain(llm: BaseChatModel, prompt: ChatPromptTemplate, tools: BaseTool) -> Runnable:
    return prompt | llm.bind_tools(tools)
