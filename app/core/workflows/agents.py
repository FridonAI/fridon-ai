from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig

from app.community.plugins import PLUGINS
from app.core.utils import llm


class Agent:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


supervisor_agent = Agent(ChatPromptTemplate.from_messages(
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
) | llm.bind_tools(list(map(lambda x: x.transport_class, PLUGINS))))
