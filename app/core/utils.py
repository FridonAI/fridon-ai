import functools

from langchain_openai import ChatOpenAI
from pydantic import Field
from pydantic.v1 import BaseModel

from app.core.utilities import BlockchainUtility, RemoteUtility


def blockchain(func):
    @functools.wraps(func)
    async def wrapper(self: BlockchainUtility, *args, **kwargs):
        request = await func(self, *args, **kwargs)
        config = kwargs.get('config')

        if not config:
            raise ValueError("Missing 'config' in kwargs")

        wallet_id = config.get("wallet_id", "")
        chat_id = config.get("chat_id", "")
        request["args"]["walletAddress"] = wallet_id

        tx = self._generate_tx(request)
        result = await self._send_and_wait(tx, wallet_id, chat_id)

        return result

    return wrapper


def remote(func):
    @functools.wraps(func)
    async def wrapper(self: RemoteUtility, *args, **kwargs):
        request = await func(self, *args, **kwargs)
        config = kwargs.get('config')

        if not config:
            raise ValueError("Missing 'config' in kwargs")

        wallet_id = config.get("wallet_id", "")
        request["args"]["walletAddress"] = wallet_id

        return self._get_remote_response(request)


llm = ChatOpenAI(model="gpt-4o", verbose=True)


class CompleteTool(BaseModel):
    """A tool to mark the current agent's work as completed with appropriate answer and return control to the main assistant,
    who can re-route the dialog based on the user's needs. It collects all tool call results and returns them as a single answer."""

    answer: str

    class Config:
        schema_extra = {
            "example": {
                "answer": "Your sol balance is 20.",
            },
            "example 2": {
                "answer": "You've successfully borrowed 10 sol on kamino",
            },
        }


class ToAssistant(BaseModel):
    """Transfer control to the assistant"""
    request: str = Field(
        description="Requests from the player."
    )

    class Config:
        schema_extra = {
            "example": {
                "request": "What are withdraw requirements?",
            }
        }


def create_modified_classes(plugins, base_class=ToAssistant):
    modified_classes = []
    for plugin in plugins:
        # Create the new class name by prepending "To"
        new_class_name = f"To{plugin.__name__}"

        # Create a new class dynamically
        new_class = type(
            new_class_name,
            (base_class,),
            {
                "__doc__": f"Transfer control to {plugin.__name__}",
                "__annotations__": base_class.__annotations__,
                "__module__": __name__,
                "query": base_class.__fields__["query"],
                "Config": base_class.Config,
            }
        )

        # Add the new class to the list
        modified_classes.append(new_class)

    return modified_classes
