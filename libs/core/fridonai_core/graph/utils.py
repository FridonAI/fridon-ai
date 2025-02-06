import json
from fridonai_core.graph.tools import CompleteTool
from langchain_core.messages import ToolMessage, AIMessage

from fridonai_core.graph.prompts import create_tools_response_finalizer_prompt
from fridonai_core.graph.states import State, SubState
from fridonai_core.graph.models import get_model
from langchain_core.output_parsers import StrOutputParser


def prepare_plugin_agent(state):
    plugin_name = state["plugin_names_to_call"].pop()
    tool_calls = state["messages"][-1].tool_calls
    for tc in filter(lambda tc: tc["name"] == plugin_name, tool_calls):
        return {
            "messages": [
                AIMessage("", tool_calls=[tc]),
                ToolMessage(
                    tool_call_id=tc["id"],
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
    answers = []
    after_human_messages = []

    structured_answers = []

    for i in range(len(messages) - 1, -1, -1):
        if messages[i].name == "Result":
            result = json.loads(messages[i].content)
            if len(result["structured_answers"]) > 0:
                structured_answers += result["structured_answers"]
            if len(result["text_answer"]) > 0:
                answers.append(result["text_answer"])
        if messages[i].type == "human":
            break
        after_human_messages.append(messages[i])

    text_answer = ""
    if len(answers) > 0:
        text_answer = "\n".join(answers)

    return {
        "final_response": {
            "structured_answers": structured_answers,
            "text_answer": text_answer,
        }
    }


def finalize_tools_response(state: SubState) -> dict:
    messages = state["messages"]
    structured_outputs = []
    text_outputs = []
    for i, message in enumerate(messages):
        if message.type == "tool" and i > 2:
            try:
                structured_outputs.append(json.loads(message.content))
            except ValueError:
                text_outputs.append(f"{message.content}")

    text_answer = ""
    if len(text_outputs) > 0:
        prompt = create_tools_response_finalizer_prompt(text_outputs)

        chain = prompt | get_model() | StrOutputParser()

        text_answer = chain.invoke({"answers": text_outputs})

    return {
        "messages": [
            AIMessage(
                "",
                tool_calls=[
                    {"id": "complete_tools", "name": CompleteTool.__name__, "args": {}}
                ],
            ),
            ToolMessage(
                tool_call_id="complete_tools",
                content=json.dumps(
                    {
                        "text_answer": text_answer,
                        "structured_answers": structured_outputs,
                    }
                ),
                name="Result",
            ),
        ],
        "used_agents": [],
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
