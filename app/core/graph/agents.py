from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig

from app.community.plugins import PLUGINS
from app.core.utils import llm, Agent, ToAssistant


transport_classes = list(map(lambda x: x.transport_class, PLUGINS))

supervisor_chain = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a supervisor tasked with managing a conversation between assistants and finally delivering the answer to the player. "
            "Your main role is to answer player's query, for that delegate tasks to the appropriate tools based on the player's query. "
            "The player is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
            "Provide detailed and concise response, don't talk too much. Don't copy paste tool's responses. "
            "\nDon't make up any information just use provided information and messages."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
) | llm.bind_tools(transport_classes)


supervisor_agent = Agent(supervisor_chain)

