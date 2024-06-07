from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

from app.core.graph.agents import create_agent
from app.core.graph.chains import create_agent_chain
from app.core.graph.prompts import create_agent_prompt, create_supervised_prompt
from app.core.graph.routers import route_plugin_agent, route_supervisor_agent
from app.core.graph.states import State
from app.core.graph.tools import CompleteTool, create_plugin_wrapper_tool
from app.core.graph.utils import prepare_plugin_agent, handle_tool_error, leave_tool
from app.core.plugins import BasePlugin


def create_graph(
    llm: BaseChatModel, plugins: list[BasePlugin], memory: BaseCheckpointSaver
):
    plugins_to_wrapped_plugins = {
        p.name: create_plugin_wrapper_tool(p, type(p).__name__) for p in plugins
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

    all_tools = [CompleteTool]
    for plugin in plugins:
        all_tools += plugin.tools
    tool_node = ToolNode(all_tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)],
        exception_key="error"
    )

    for plugin in plugins:
        agent_chain = create_agent_chain(
            llm,
            create_agent_prompt(plugin.name, plugin.full_description),
            tools=plugin.tools + [CompleteTool],
        )

        agent = create_agent(agent_chain, plugin.name)

        workflow.add_node("Enter"+plugin.name, prepare_plugin_agent)
        workflow.add_node(plugin.name, agent)
        workflow.add_edge("Enter"+plugin.name, plugin.name)
        workflow.add_edge("tool_node", plugin.name)
        workflow.add_conditional_edges(
            plugin.name,
            route_plugin_agent,
            {
                "tool_node": "tool_node",
                "leave_tool": "leave_tool",
                "supervisor": "supervisor"
            }
        )

    def _route_supervisor_agent_wrapper(state):
        return route_supervisor_agent(state, wrapped_plugins_to_plugins)

    workflow.add_conditional_edges(
        "supervisor",
        _route_supervisor_agent_wrapper,
        {**{
            "Enter"+plugin.name: "Enter"+plugin.name
            for plugin in plugins
        }, END: END}
    )

    workflow.add_node("leave_tool", leave_tool)
    workflow.add_edge("leave_tool", "supervisor")

    workflow.add_node("tool_node", tool_node)

    workflow.set_entry_point("supervisor")

    return workflow.compile(checkpointer=memory)
