from langchain_core.prompts import ChatPromptTemplate


def create_supervised_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a supervisor tasked with managing a conversation between assistants and finally delivering the answer to the player. "
                "Your main role is to answer player's query, for that delegate tasks to the appropriate tools based on the player's query. "
                "The player is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
                "Provide detailed and concise response, don't talk too much. Don't copy paste tool's responses. "
                "\nDon't make up any information just use provided information and messages. If some tool wasn't able to do its job say it don't pretend that everything is fine."
                "If no tools are appropriate for the query just respond yourself and go to the end state.",
            ),
            ("placeholder", "{messages}"),
        ]
    )


def create_agent_prompt(name: str, description: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are a specialized assistant named '{name}' for handling user's requests using the provided tools."
                "The primary assistant delegates work to you whenever the player needs help with their account information. "
                "Use appropriate tools to satisfy all user's needs. "
                "When you think that you gathered all the necessary information, call the *Complete* tool to let the primary assistant take control."
                f"Your description: {description}"
                "\nIf you get the message which isn't your job, say it and just call CompleteTool.",
            ),
            ("placeholder", "{messages}"),
        ]
    )
