import json
from fridonai_core.graph.tools import CompleteTool
from langchain_core.messages import ToolMessage, AIMessage
from fridonai_core.graph.states import State, SubState


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
                content="There was an error while executing the tool. Try again.",
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

    return {
        "final_response": {
            "structured_answers": structured_answers,
            "text_answer": messages[-1].content,
        }
    }


def finalize_tools_response(state: SubState) -> dict:
    messages = state["messages"]
    structured_outputs = []
    text_outputs = []
    for i, message in enumerate(messages):
        if message.type == "tool" and i > 2:
            try:
                str_data = json.loads(message.content)
                if "structured_data" in str_data and str_data["structured_data"]:
                    structured_outputs.append(json.loads(message.content))
                else:
                    text_outputs.append(f"{str_data}")
            except ValueError:
                text_outputs.append(f"{message.content}")
        if (
            message.type == "ai"
            and len(message.tool_calls) == 0
            and not message.name
            and message.content != "Complete"
        ):
            text_outputs.append(f"{message.content}")

    text_answer = "\n\n".join(text_outputs)
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
        "used_agents": state["used_agents"],
    }
