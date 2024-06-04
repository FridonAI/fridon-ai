from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

from app.core.graph.agents import create_agent
from app.core.graph.chains import create_agent_chain
from app.core.graph.prompts import create_agent_prompt, create_supervised_prompt
from app.core.graph.states import State
from app.core.graph.tools import CompleteTool, create_plugin_wrapper_tool
from app.core.plugins import BasePlugin


def create_graph(
    llm: BaseChatModel, plugins: list[BasePlugin], memory: BaseCheckpointSaver
):
    plugins_to_wrapped_plugins = {
        p.name: create_plugin_wrapper_tool(type(p)) for p in plugins
    }
    wrapped_plugins_to_plugins = {
        wp.__name__: pname for pname, wp in plugins_to_wrapped_plugins.items()
    }

    workflow = StateGraph(State)

    supervisor_agent = create_agent(
        create_agent_chain(
            llm,
            prompt=create_supervised_prompt(),
            tools=list(plugins_to_wrapped_plugins.values()),
        )
    )

    workflow.add_node("supervisor", supervisor_agent)

    def prepare_plugin_agent(state):
        tool_call = state["messages"][-1].tool_calls[0]
        return {
            "messages": [state["messages"][-1], ToolMessage(tool_call_id=tool_call["id"], content="")]
        }

    def route_plugin_agent(
            state,
    ) -> str:
        route = tools_condition(state)
        if route == END:
            return 'supervisor'
        tool_calls = state["messages"][-1].tool_calls
        did_cancel = any(tc["name"] == CompleteTool.__name__ for tc in tool_calls)
        if did_cancel:
            return 'supervisor'
        return "tool_node"

    def route_supervisor_agent(state: State) -> list[str]:
        route = tools_condition(state)
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls
        if tool_calls:
            return ["Enter"+wrapped_plugins_to_plugins[tc["name"]] for tc in tool_calls]

        raise ValueError("Invalid route")

    all_tools = []
    for plugin in plugins:
        all_tools += plugin.tools
    tool_node = ToolNode(all_tools)

    for plugin in plugins:
        agent_chain = create_agent_chain(
            llm,
            create_agent_prompt(plugin.name, plugin.description),
            tools=plugin.tools + [CompleteTool],
        )

        agent = create_agent(agent_chain)

        workflow.add_node("Enter"+plugin.name, prepare_plugin_agent)
        workflow.add_node(plugin.name, agent)
        workflow.add_edge("Enter"+plugin.name, plugin.name)
        workflow.add_edge("tool_node", plugin.name)
        workflow.add_conditional_edges(
            plugin.name,
            route_plugin_agent,
            {
                "tool_node": "tool_node",
                "supervisor": "supervisor"
            }
        )

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor_agent,
        {**{
            "Enter"+plugin.name: "Enter"+plugin.name
            for plugin in plugins
        }, END: END}
    )
    workflow.add_node("tool_node", tool_node)

    workflow.set_entry_point("supervisor")

    return workflow.compile(checkpointer=memory)
