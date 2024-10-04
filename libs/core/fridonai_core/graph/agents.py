from langchain_core.runnables import Runnable, RunnableConfig


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


def create_agent(runnable: Runnable, name: str = "Agent") -> Agent:
    if name == "Agent":
        return SupervisorAgent(runnable, "Agent")
    return Agent(runnable, name)
