from operator import add
from typing import Annotated, List, TypedDict, Union

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    used_agents: Annotated[list[str], add]
    final_response: Union[dict, None]


class SubState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    used_agents: list[str]


def attach_tool_response_to_tool(state: State) -> dict:
    messages = state["messages"]

    tool_resp = messages[1]
    tool_resp.content = messages[-1].content
    tool_resp.name = "Result"
    return {
        "messages": [
            tool_resp,
        ],
        "used_agents": state["used_agents"],
    }
