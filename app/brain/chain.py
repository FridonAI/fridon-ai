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
    CoinSearcherAdapter, DiscordActionAdapter,
)
from app.brain.templates import (
    defi_stake_borrow_lend_extract_prompt,
    defi_talker_prompt,
    defi_balance_extract_prompt,
    defi_transfer_prompt, response_generator_prompt, coin_search_prompt, discord_action_prompt
)
from app.settings import settings

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


def get_chat_history(session_id):
    chat_history = PostgresChatMessageHistory(
        connection_string=settings.POSTGRES_DB_URL,
        session_id=session_id
    )
    return chat_history


defi_stake_borrow_lend_extract_chain = (
    defi_stake_borrow_lend_extract_prompt
    | llm
    | DefiStakeBorrowLendAdapter.parser()
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

discord_action_chain = (
    discord_action_prompt
    | llm
    | DiscordActionAdapter.parser()
)



defi_talker_chain = RunnableWithMessageHistory(
    (
        defi_talker_prompt
        | llm
        | DefiTalkerAdapter.parser()
    ),
    get_chat_history,
    input_messages_key="query",
    history_messages_key="history",
)


coin_search_chain = RunnableWithMessageHistory(
    (
        {
            "query": lambda x: x["query"],
            "context": RunnableLambda(lambda x: x["query"]) | retriever,
            "history": lambda x: x["history"]
        }
        | coin_search_prompt
        | llm
        | CoinSearcherAdapter.parser()
    ),
    get_chat_history,
    input_messages_key="query",
    history_messages_key="history",
)

response_generator_chain = RunnableWithMessageHistory(
    (response_generator_prompt | llm | StrOutputParser()),
    get_chat_history,
    input_messages_key="query",
    history_messages_key="history",
)


branch = RunnableBranch(
    (lambda x: x['category'] == 'DefiStakeBorrowLend', defi_stake_borrow_lend_extract_chain),
    (lambda x: x['category'] == 'DeFiBalance', defi_balance_extract_chain),
    (lambda x: x['category'] == 'DeFiTransfer', defi_transfer_chain),
    (lambda x: x['category'] == 'CoinSearch', coin_search_chain),
    defi_talker_chain,
)


async def generate_response(chat_id, wallet_id, query):
    print("Generate response", query)
    memory = get_chat_history(chat_id)

    async def get_response(adapter: Adapter):
        return await adapter.get_response(chat_id, wallet_id)

    question_answer_chain = (
            {"query": lambda x: x["query"], "category": RunnableLambda(get_category)}
            | branch
            | {"response": RunnableLambda(get_response), "obj": lambda x: x}
    )
    chain_resp = await question_answer_chain.ainvoke(
        {"query": query},
        config={"configurable": {"session_id": chat_id}}
    )

    obj = chain_resp["obj"]
    response = chain_resp["response"]

    if isinstance(obj, (CoinSearcherAdapter, DefiTalkerAdapter)):
        final_response = response
    else:
        final_response = await response_generator_chain.ainvoke(
            {"query": query, "response": response},
            config={"configurable": {"session_id": chat_id}}
        )

    memory.add_user_message(query)
    memory.add_ai_message(final_response)

    print("Response", final_response)
    return final_response
