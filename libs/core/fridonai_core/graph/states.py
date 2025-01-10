from operator import add
from typing import Annotated, List, TypedDict, Union

from langchain_core.messages import AnyMessage, ToolMessage
from langgraph.graph import add_messages

from fridonai_core.graph.tools import FinalResponse
from fridonai_core.graph.tools import CompleteTool


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    used_agents: Annotated[list[str], add]
    final_response: Union[FinalResponse, None]

class SubState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


def attach_tool_response_to_tool(state: State) -> dict:
    tool_calls = state["messages"][-1].tool_calls
    for tc in filter(lambda tc: tc["name"] == CompleteTool.__name__, tool_calls):
        tool_id = state["messages"][0].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(tool_call_id=tool_id, content=tc["args"], name="Result"),
            ]
        }