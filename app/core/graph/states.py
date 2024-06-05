from operator import add
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    used_agents: Annotated[list[str], add]
