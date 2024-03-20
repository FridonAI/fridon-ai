import asyncio

from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_openai import ChatOpenAI

from app.brain.router import get_category
from app.brain.schema import (
    DefiStakeBorrowLendAdapter, DefiTransferAdapter, DefiBalanceAdapter, DefiTalkerAdapter,
)
from app.brain.templates import (
    defi_stake_borrow_lend_extract_prompt,
    defi_talker_prompt,
    defi_balance_extract_prompt,
    defi_transfer_prompt
)

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


branch = RunnableBranch(
    (lambda x: x['category'] == 'DefiStakeBorrowLend', defi_stake_borrow_lend_extract_chain),
    (lambda x: x['category'] == 'DeFiBalance', defi_balance_extract_chain),
    (lambda x: x['category'] == 'DeFiTransfer', defi_transfer_chain),
    defi_talker_chain,
)


async def generate_response(chat_id, wallet_id, query):
    print("Generate response", query)
    full_chain = (
            {"query": lambda x: x["query"], "category": RunnableLambda(get_category)}
            | branch
            | RunnableLambda(lambda x: asyncio.run(x.get_response(chat_id, wallet_id)))
    )

    response = await full_chain.ainvoke({"query": query})

    print("Response", response)
    return response
