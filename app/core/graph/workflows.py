from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition

from app.core.graph.agents import supervisor_agent
from app.core.graph.states import State
from app.community.plugins import PLUGINS

memory = SqliteSaver.from_conn_string(":memory:")


transport_class_to_agent_name = {plugin.transport_class.__name__: plugin.name for plugin in PLUGINS}

def route_supervisor_agent(
    state: State,
) -> list:
    route = tools_condition(state)
    if route == END:
        return END
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        return [transport_class_to_agent_name[tc["name"]] for tc in tool_calls]

    raise ValueError("Invalid route")


workflow = StateGraph(State)


workflow.add_node("supervisor", supervisor_agent)


for plugin in PLUGINS:
    workflow.add_node(plugin.name, plugin.agent)
    workflow.add_edge(plugin.name, "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    route_supervisor_agent,
    {plugin_name: plugin_name for plugin_name in transport_class_to_agent_name.values()}.update({END: END})
)
workflow.set_entry_point("supervisor")

graph = workflow.compile(
    checkpointer=memory
)