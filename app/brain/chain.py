from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_openai import ChatOpenAI

from app.brain.router import get_category
from app.brain.schema import DefiStakeBorrowLendParameters, DefiBalanceParameters
from app.brain.templates import defi_stake_borrow_lend_extract_prompt, defi_talker_prompt, defi_balance_extract_prompt
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


defi_stake_borrow_lend_extract_chain = (
    defi_stake_borrow_lend_extract_prompt
    | llm
)

defi_talker_chain = (
    defi_talker_prompt
    | llm
)

defi_balance_extract_chain = (
    defi_balance_extract_prompt
    | llm
)

str_parser = StrOutputParser()


branch = RunnableBranch(
    (lambda x: x['category'] == 'DefiStakeBorrowLend', defi_stake_borrow_lend_extract_chain | DefiStakeBorrowLendParameters.parser()),
    (lambda x: x['category'] == 'DeFiBalance', defi_balance_extract_chain | DefiBalanceParameters.parser()),
    defi_talker_chain | str_parser,
)

full_chain = {"query": lambda x: x["query"], "category": RunnableLambda(get_category)} | branch


def generate_response(query):
    print("Generate response", query)
    response = full_chain.invoke({'query': query})
    print("Response", response)
    return response
