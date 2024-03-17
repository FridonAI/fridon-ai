from langchain_core.prompts import ChatPromptTemplate

defi_stake_borrow_lend_extract_template = {
    "system": """You are the best defi parameters extractor from query. You've to determine following parameters from the given query: provider, operation, currency and amount.
Return following json string: "{{status: boolean, "provider": "string" | null, "operation": "string" | null, "currency": "string" | null, "amount": number | null, "comment": "string" | null}}"
E.x. "I want to lend 100 usdc on kamino" you've to return "{{status:"true", "provider": "kamino", "operation": "lend", "currency': "usdc", "amount": 100}}"
"provider" must be mentioned.
"operation" must be mentioned.
"currency" must be mentioned.
"amount" must be mentioned.
If any must to parameters is unknown then return "{{status: false, comment: "..."}}" Comment is which parameters you can't extract.
Extract names as lowercase.
"""
}


defi_talker_template = {
    "system": """Just answer the question from your knowledge."""
}


defi_balance_extract_template = {
    "system": """You are the best balance parameters extractor from query. You've to determine following parameters from the given query: provider, operation, currency.
Return following json string: "{{"status": boolean, "provider": "string" | null, "operation": "string" | null, "currency": "string" | null, "comment": "string" | null}}"
If "provider" is not mentioned then default value is "all".
If "operation" is not mentioned then default value is "walletbalance".
"Currency" must be mentioned.
If any must to parameters is unknown then return: "{{status: false, comment: "..."}}" Comment is which parameters you can't extract.
E.x. "How much usdc is lend on my Kamino?" you've to return "{{"provider": "kamino", "operation": "lend", "currency': "usdc"}}"
Extract names as lowercase.
"""
}


defi_stake_borrow_lend_extract_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", defi_stake_borrow_lend_extract_template['system']),
        ("human", "{query}"),
    ]
)

defi_balance_extract_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", defi_balance_extract_template['system']),
        ("human", "{query}"),
    ]
)


defi_talker_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", defi_talker_template['system']),
        ("human", "{query}"),
    ]
)
