from langchain_core.messages import ToolMessage


def prepare_plugin_agent(state):
    tool_call = state["messages"][-1].tool_calls[0]
    return {
        "messages": [state["messages"][-1], ToolMessage(tool_call_id=tool_call["id"], content="")]
    }


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }
