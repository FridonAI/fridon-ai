from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition

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

    for plugin in plugins:
        plugin_agent = create_agent(
            create_agent_chain(
                llm,
                create_agent_prompt(plugin.name, plugin.description),
                tools=plugin.tools + [CompleteTool],
            )
        )
        workflow.add_node(plugin.name, plugin_agent)
        workflow.add_edge(plugin.name, "supervisor")

    def route_supervisor_agent(state: State) -> list[str]:
        route = tools_condition(state)
        if route == END:
            return END
        tool_calls = state["messages"][-1].tool_calls
        if tool_calls:
            return [wrapped_plugins_to_plugins[tc["name"]] for tc in tool_calls]

        raise ValueError("Invalid route")

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor_agent,
        {
            plugin.name: plugin.name
            for plugin in plugins
        }.update({END: END}),
    )

    workflow.set_entry_point("supervisor")

    return workflow.compile(checkpointer=memory)
