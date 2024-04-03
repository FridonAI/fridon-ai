from app.brain.chain import get_chain, get_chat_history, get_error_chain, get_response_generator_chain
from pydantic.v1 import BaseModel

from app.brain.router import get_category
from app.brain.schema import CoinSearcherAdapter, DefiTalkerAdapter, MediaQueryExtractAdapter


class Chat:
    def __init__(self, chat_id: str, wallet_id: str, personality: str) -> None:
        self.chat_id = chat_id
        self.wallet_id = wallet_id
        self.personality = personality
        self.memory = get_chat_history(self.chat_id)

    async def process(
            self,
            message: str,
    ) -> str | BaseModel:

        try:
            category = get_category(message)
            chain = get_chain(category, self.personality)
            adapter = await chain.ainvoke({"query": message, "wallet_id": self.wallet_id}, config={"configurable": {"session_id": self.chat_id}})

            if category in [None, 'OffTopic']:
                return adapter
            print(f"Got adapter", adapter)
            response = await adapter.get_response(self.chat_id, self.wallet_id, self.personality)

            if isinstance(adapter, (CoinSearcherAdapter, DefiTalkerAdapter, MediaQueryExtractAdapter)):
                final_response = response

            else:
                final_response = await get_response_generator_chain(self.personality).ainvoke(
                    {"query": message, "response": response},
                    config={"configurable": {"session_id": self.chat_id}}
                )

            self.memory.add_user_message(message)
            self.memory.add_ai_message(final_response)
        except Exception as e:
            print("Error in Chat.process", e)
            chain = get_error_chain(self.personality)
            final_response = await chain.ainvoke({"query": message})
            # raise e

        return final_response


