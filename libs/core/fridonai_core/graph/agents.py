from pydantic import BaseModel

from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from fridonai_core.plugins.tools.base import BaseTool
from fridonai_core.graph.states import SubState
from fridonai_core.graph.models import get_model
from fridonai_core.graph.routers import route_plugin_agent
from fridonai_core.graph.utils import handle_tool_error, finalize_tools_response


class Agent:
    def __init__(self, runnable: Runnable, name: str = "Agent"):
        self.name = name
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
        return {
            "messages": result,
            "used_agents": [self.name] if self.name != "Agent" else [],
        }


class SupervisorAgent(Agent):
    def __call__(self, state, config: RunnableConfig):
        result = super().__call__(state, config)["messages"]
        grouped_tool_calls = {}

        for tc in result.tool_calls:
            tool_name = tc["name"]
            if tool_name not in grouped_tool_calls:
                grouped_tool_calls[tool_name] = {**tc, "args": {}}
            for key in tc["args"]:
                if key not in grouped_tool_calls[tool_name]["args"]:
                    grouped_tool_calls[tool_name]["args"][key] = tc["args"][key]
                else:
                    grouped_tool_calls[tool_name]["args"][key] += tc["args"][key]

        tcs = list(grouped_tool_calls.values())

        result.tool_calls = [] if len(tcs) == 0 else [tcs[0]]

        return {"messages": result, "used_agents": []}


def create_agent_chain(
    llm: BaseChatModel,
    prompt: ChatPromptTemplate,
    tools: list[BaseTool | type[BaseModel]],
    always_tool_call=False,
) -> Runnable:
    if always_tool_call:
        return prompt | llm.bind_tools(
            tools, tool_choice="any", parallel_tool_calls=True
        )
    return prompt | llm.bind_tools(tools, parallel_tool_calls=True)


def create_agent(
    prompt: ChatPromptTemplate,
    tools: list[BaseTool | type[BaseModel]],
    always_tool_call=False,
    name: str = "Agent",
    llm=get_model("gpt-4o"),
) -> Agent:
    runnable = create_agent_chain(llm, prompt, tools, always_tool_call=always_tool_call)

    if name == "Agent":
        return SupervisorAgent(runnable, name="Agent")

    agent = Agent(runnable, name=name)
    graph = StateGraph(SubState)

    tool_node = ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

    agent_node_name = name.lower() + "Agent"
    agent_tools_node_name = agent_node_name + "Tools"
    agent_tools_finalizer_node_name = agent_tools_node_name + "Finalizer"

    graph.add_node(agent_node_name, agent)
    graph.add_node(agent_tools_node_name, tool_node)
    graph.add_node(agent_tools_finalizer_node_name, finalize_tools_response)

    graph.add_edge(agent_tools_node_name, agent_node_name)

    graph.add_conditional_edges(
        agent_node_name,
        route_plugin_agent,
        {
            "tool_node": agent_tools_node_name,
            END: agent_tools_finalizer_node_name,
        },
    )

    graph.set_entry_point(agent_node_name)

    graph = graph.compile()

    return graph
