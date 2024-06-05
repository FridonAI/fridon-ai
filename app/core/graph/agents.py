from langchain_core.runnables import Runnable, RunnableConfig


class Agent:
    def __init__(self, runnable: Runnable, name: str = 'Agent'):
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
        return {"messages": result, "used_agents": [self.name] if self.name != "Agent" else []}


def create_agent(runnable: Runnable, name: str = 'Agent') -> Agent:
    return Agent(runnable, name)
