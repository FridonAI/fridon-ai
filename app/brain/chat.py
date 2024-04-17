import json

from app.brain.chain import get_chain, get_chat_history, get_error_chain, get_response_generator_chain, \
    get_question_condenser_chain
from pydantic.v1 import BaseModel

from app.brain.router import get_category
from app.brain.schema import CoinProjectSearcherAdapter, DefiTalkerAdapter, MediaQueryExtractAdapter, \
    CoinChartSimilarityAdapter, CoinTAQueryExtractAdapter


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
            condense_question_chain = get_question_condenser_chain()
            condense_question_chain = condense_question_chain.with_config(run_name="CondenseQuestion")
            condensed_message = await condense_question_chain.ainvoke({"query": message}, config={"configurable": {"session_id": self.chat_id}})
            print("Condensed message", condensed_message)
            category = get_category(condensed_message)
            print("Category", category)
            chain = get_chain(category, self.personality)
            print("Took chain")
            adapter = await chain.ainvoke({"query": condensed_message, "wallet_id": self.wallet_id}, config={"configurable": {"session_id": self.chat_id}})

            if category in [None, 'OffTopic']:
                return adapter
            print(f"Got adapter", adapter)
            response = await adapter.get_response(self.chat_id, self.wallet_id, self.personality)

            if isinstance(adapter, (CoinProjectSearcherAdapter, DefiTalkerAdapter, MediaQueryExtractAdapter)):
                final_response = response
            elif isinstance(adapter, CoinTAQueryExtractAdapter) and self.personality == "Normal":
                final_response = response
            else:
                final_response = await get_response_generator_chain(self.personality).ainvoke(
                    {"query": condensed_message, "response": response},
                    config={"configurable": {"session_id": self.chat_id}}
                )
                if isinstance(adapter, CoinChartSimilarityAdapter):
                    final_response = json.dumps({**json.loads(response), "message": final_response})

            self.memory.add_user_message(message)
            self.memory.add_ai_message(final_response)
        except Exception as e:
            print("Error in Chat.process", e)
            chain = get_error_chain(self.personality)
            # final_response = await chain.ainvoke({"query": message})
            raise e

        return final_response


