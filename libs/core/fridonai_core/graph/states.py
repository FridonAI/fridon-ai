from operator import add
from typing import Annotated, List, TypedDict, Union

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

from fridonai_core.graph.tools import FinalResponse


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    used_agents: Annotated[list[str], add]
    final_response: Union[FinalResponse, None]
