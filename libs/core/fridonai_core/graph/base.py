from typing import Literal, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import HumanMessage

from fridonai_core.graph.agents import create_agent
from fridonai_core.graph.chains import create_agent_chain
from fridonai_core.graph.prompts import create_agent_prompt, create_supervised_prompt
from fridonai_core.graph.routers import route_plugin_agent, route_supervisor_agent
from fridonai_core.graph.states import State
from fridonai_core.graph.tools import CompleteTool, create_plugin_wrapper_tool
from fridonai_core.graph.utils import (
    generate_structured_response,
    handle_tool_error,
    leave_tool,
    prepare_plugin_agent,
)
from fridonai_core.plugins import BasePlugin
from settings import settings


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
            tools=[*list(plugins_to_wrapped_plugins.values())],
            always_tool_call=False,
        )
    )

    workflow.add_node("supervisor", supervisor_agent)

    for plugin in plugins:
        agent_chain = create_agent_chain(
            llm,
            create_agent_prompt(
                plugin.name,
                plugin.full_description(tool_descriptions=False),
                plugin.output_format,
            ),
            tools=plugin.tools + [CompleteTool],
            always_tool_call=True,
        )

        tool_node = ToolNode(plugin.tools + [CompleteTool]).with_fallbacks(
            [RunnableLambda(handle_tool_error)], exception_key="error"
        )

        agent = create_agent(agent_chain, plugin.slug)

        workflow.add_node("Enter" + plugin.name, prepare_plugin_agent)
        workflow.add_node(plugin.name, agent)
        workflow.add_edge("Enter" + plugin.name, plugin.name)
        workflow.add_node(plugin.name + "_tools", tool_node)
        workflow.add_edge(plugin.name + "_tools", plugin.name)
        workflow.add_conditional_edges(
            plugin.name,
            route_plugin_agent,
            {
                "tool_node": plugin.name + "_tools",
                "leave_tool": "leave_tool",
                "supervisor": "supervisor",
            },
        )

    def _route_supervisor_agent_wrapper(state):
        return route_supervisor_agent(state, wrapped_plugins_to_plugins)

    workflow.add_conditional_edges(
        "supervisor",
        _route_supervisor_agent_wrapper,
        {
            **{"Enter" + plugin.name: "Enter" + plugin.name for plugin in plugins},
            "respond": "respond",
        },
    )
    workflow.add_node("respond", generate_structured_response)
    workflow.add_node("leave_tool", leave_tool)
    workflow.add_edge("leave_tool", "supervisor")
    workflow.add_edge("respond", END)

    workflow.set_entry_point("supervisor")

    return workflow.compile(checkpointer=memory)


async def generate_response(
    message: str, 
    plugins: list[BasePlugin],
    llm: BaseChatModel,
    config: dict,
    memory: Literal['postgres'] = 'postgres',
    return_used_agents: bool = True,
):
    if memory != 'postgres':
        raise ValueError('Only postgres is supported for now')
    
    async with AsyncPostgresSaver.from_conn_string(
        settings.POSTGRES_DB_URL, pipeline=False
    ) as memory:
        await memory.setup()
        graph = create_graph(llm, plugins, memory)
        graph_config = {
            "configurable": config
        }
        response = ""
        async for s in graph.astream(
            {
                "messages": [HumanMessage(content=message)],
            },
            graph_config,
            stream_mode="values",
        ):
            if "__end__" not in s:
                response = s["messages"][-1]
                response.pretty_print()

        graph_state = await graph.aget_state(graph_config)
        final_response = graph_state.values.get("final_response")
        if return_used_agents:
            used_agents = list(set(graph_state.values.get("used_agents", [])))
            return final_response, used_agents
        return final_response
