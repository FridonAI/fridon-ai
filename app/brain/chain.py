import asyncio

from langchain_community.chat_message_histories.postgres import PostgresChatMessageHistory
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from app.adapters.coins import retriever
from app.brain.router import get_category
from app.brain.schema import (
    DefiStakeBorrowLendAdapter, DefiTransferAdapter, DefiBalanceAdapter, DefiTalkerAdapter, Adapter,
)
from app.brain.templates import (
    defi_stake_borrow_lend_extract_prompt,
    defi_talker_prompt,
    defi_balance_extract_prompt,
    defi_transfer_prompt, response_generator_prompt, coin_search_prompt
)
from app.settings import settings

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


defi_stake_borrow_lend_extract_chain = (
    defi_stake_borrow_lend_extract_prompt
    | llm
    | DefiStakeBorrowLendAdapter.parser()
)

defi_talker_chain = (
    defi_talker_prompt
    | llm
    | DefiTalkerAdapter.parser()
)

defi_balance_extract_chain = (
    defi_balance_extract_prompt
    | llm
    | DefiBalanceAdapter.parser()
)


defi_transfer_chain = (
    defi_transfer_prompt
    | llm
    | DefiTransferAdapter.parser()
)

response_generator_chain = (
    response_generator_prompt
    | llm
    | StrOutputParser()
)

coin_search_chain = (
    {"query": lambda x: x["query"], "context": RunnableLambda(lambda x: x["query"]) | retriever}
    | coin_search_prompt
    | llm
    | StrOutputParser()
)


branch = RunnableBranch(
    (lambda x: x['category'] == 'DefiStakeBorrowLend', defi_stake_borrow_lend_extract_chain),
    (lambda x: x['category'] == 'DeFiBalance', defi_balance_extract_chain),
    (lambda x: x['category'] == 'DeFiTransfer', defi_transfer_chain),
    (lambda x: x['category'] == 'CoinSearch', coin_search_chain),
    defi_talker_chain,
)


def _get_chat_history(self, chat_id):
    chat_history = PostgresChatMessageHistory(
        connection_string=settings.POSTGRES_DB_URL,
        session_id=chat_id
    )
    return chat_history


def get_chat_history(session_id):
    chat_history = PostgresChatMessageHistory(
        connection_string=settings.POSTGRES_DB_URL,
        session_id=session_id
    )
    return chat_history


async def generate_response(chat_id, wallet_id, query):
    print("Generate response", query)
    memory = get_chat_history(chat_id)
    response_generator_with_message_history = RunnableWithMessageHistory(
        response_generator_chain,
        get_chat_history,
        input_messages_key="query",
        history_messages_key="history",
    )

    async def get_response(adapter: Adapter):
        return await adapter.get_response(chat_id, wallet_id)

    question_answer_chain = (
            {"query": lambda x: x["query"], "category": RunnableLambda(get_category)}
            | branch
            | RunnableBranch((lambda x: isinstance(x, str), RunnableLambda(lambda x: x)), RunnableLambda(get_response))
    )
    response = await question_answer_chain.ainvoke({"query": query})

    final_response = await response_generator_with_message_history.ainvoke(
        {"query": query, "response": response},
        {"configurable": {"session_id": chat_id}}
    )

    memory.add_user_message(query)
    memory.add_ai_message(final_response)

    print("Response", final_response)
    return final_response
