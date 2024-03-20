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

defi_transfer_template = {
    "system": """You are the best token transfer parameters extractor from query. You've to determine following parameters from the given query: token, wallet.
Return following json string: "{{"status": boolean, "currency": "string" | null, "wallet": "string" | null}}"
"wallet" must be mentioned.
"currency" must be mentioned.
If any must to parameters is unknown then return: "{{status: false, comment: "..."}}" Comment is which parameters you can't extract.
E.x. "Transfer 100 usdc to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD" you've to return "{{"currency": "usdc", "wallet": "2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD"}}"
Extract parameter names as lowercase.
"""
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

response_generator_template = {
    "system": """You are the best response generator from adapter response. You've to generate response from the given query.
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

defi_transfer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", defi_transfer_template['system']),
        ("human", "{query}"),
    ]
)


defi_talker_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", defi_talker_template['system']),
        ("human", "{query}"),
    ]
)

response_generator_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", response_generator_template['system']),
        ("human", "{response}"),
    ]
)