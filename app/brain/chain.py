from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_openai import ChatOpenAI

from app.adapters.adapter import AdapterResolver
from app.brain.router import get_category
from app.brain.schema import (
    DefiStakeBorrowLendParameters,
    DefiBalanceParameters,
    DefiTransferParameters, DefiTalkerParameters
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
    | DefiStakeBorrowLendParameters.parser()
)

defi_talker_chain = (
    defi_talker_prompt
    | llm
    | DefiTalkerParameters.parser()
)

defi_balance_extract_chain = (
    defi_balance_extract_prompt
    | llm
    | DefiBalanceParameters.parser()
)


defi_transfer_chain = (
    defi_transfer_prompt
    | llm
    | DefiTransferParameters.parser()
)


branch = RunnableBranch(
    (lambda x: x['category'] == 'DefiStakeBorrowLend', defi_stake_borrow_lend_extract_chain),
    (lambda x: x['category'] == 'DeFiBalance', defi_balance_extract_chain),
    (lambda x: x['category'] == 'DeFiTransfer', defi_transfer_chain),
    defi_talker_chain,
)


async def generate_response(chat_id, wallet_id, query):
    print("Generate response", query)

    full_chain = {"query": lambda x: x["query"], "category": RunnableLambda(get_category)} | branch | RunnableLambda(AdapterResolver(chat_id, wallet_id).call)

    response = await full_chain.ainvoke({"query": query})

    print("Response", response)
    return response
