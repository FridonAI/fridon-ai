from langchain_core.prompts import ChatPromptTemplate
from pydantic.v1 import BaseModel

from app.core.tools import BaseTool
from app.core.utils import CompleteTool, llm, ToAssistant
from app.core.workflows.agents import Agent


class BasePlugin(BaseModel):
    name: str
    description: str
    tools: type[list[BaseTool]]

    def create_agent(self):
        chain = self._create_chain()
        return Agent(chain)

    def _create_chain(self):
        chain = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"You are a specialized assistant named '{self.name}' for handling user's requests using the provided tools."
                    "The primary assistant delegates work to you whenever the player needs help with their account information. "
                    "Use appropriate tools to satisfy all user's needs. "
                    "When you think that you gathered all the necessary information, call the *Complete* tool to let the primary assistant take control."
                    f"Your description: {self.description}"
                )
            ]
        ) | llm.bind_tools(self.tools, [CompleteTool])
        return chain

    @property
    def transport_class(self, base_class=ToAssistant):
        new_class_name = f"To{self.__name__}"

        # Create a new class dynamically
        new_class = type(
            new_class_name,
            (base_class,),
            {
                "__doc__": f"Transfer control to {self.__name__}",
                "__annotations__": base_class.__annotations__,
                "__module__": __name__,
                "request": base_class.__fields__["request"],
                "Config": base_class.Config,
            }
        )

        return new_class
