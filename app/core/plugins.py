from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic.v1 import BaseModel

from app.core.tools import BaseTool
from app.core.utils import CompleteTool, llm, ToAssistant, Agent


class BasePlugin(BaseModel):
    name: str
    description: str
    tools: type[list[BaseTool]]

    @property
    def agent(self):
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
                ),
                ("placeholder", "{messages}"),
            ]
        ) | llm.bind_tools(self.tools + [CompleteTool])
        return chain

    @property
    def transport_class(self):
        new_class_name = f"To{self.name}Plugin"
        print("Clsnm", new_class_name)

        class Config(ToAssistant.Config):
            pass

        new_class_attrs = {
            "__doc__": f"Transfer control to {self.name} assistant",
            "__annotations__": ToAssistant.__annotations__.copy(),
            "__module__": __name__,
            "Config": Config,
        }
        new_class_attrs["request"] = ToAssistant.__fields__["request"].default

        # Create a new class dynamically
        new_class = type(
            new_class_name,
            (ToAssistant,),
            new_class_attrs
        )
        print("aeeee", type(new_class))

        return new_class
