import json
from fridonai_core.graph.tools import FinalTextResponse
from langchain_core.messages import ToolMessage, AIMessage

from fridonai_core.graph.models import create_structured_output_model
from fridonai_core.graph.states import State
from fridonai_core.graph.tools import CompleteTool
import ast


def prepare_plugin_agent(state):
    tool_call = state["messages"][-1].tool_calls[0]
    return {
        "messages": [
            AIMessage("", tool_calls=[tool_call]),
            ToolMessage(
                tool_call_id=tool_call["id"],
                content="Resuming dialog with agent, do your job and generate response for given messages.",
            ),
        ]
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


def generate_final_response(state: State):
    messages = state["messages"]
    result_messages = []
    after_human_messages = []

    structured_answers = []

    for i in range(len(messages) - 1, -1, -1):
        if messages[i].name == "Result":
            result = messages[i].content
            result = ast.literal_eval(result)
            if result["is_json"]:
                structured_answers.append(result["answer"])
            else:
                result_messages.append(messages[i])
                result_messages.append(messages[i - 1])
        if messages[i].type == "human":
            break
        after_human_messages.append(messages[i])

    final_text_response_model = create_structured_output_model(FinalTextResponse)
    if len(result_messages) == 0 and len(structured_answers) != 0:
        return {
            "final_response": {
                "structured_answers": structured_answers,
                "text_answer": None,
            }
        }
    response = final_text_response_model.invoke(
        result_messages[::-1] if len(result_messages) > 0 else after_human_messages
    )
    return {
        "final_response": json.dumps(
            {
                "structured_answers": structured_answers,
                "text_answer": response.text_answer,
            }
        )
    }


def leave_tool(state) -> dict:
    messages = []
    if state["messages"][-1].tool_calls:
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "messages": messages,
    }
