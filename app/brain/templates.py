from langchain_core.prompts import ChatPromptTemplate

BLOCKCHAIN_EXTRACT_TEMPLATE = {
    "system": """You are the best parameters extractor from query. You've to determine following parameters from the given query: provider, operation, currency and amount.
Return following json string: "{"provider": "string", "operation": "string", "currency": "string", "amount": number}"
E.x. "I want to lend 100 usdc on kamino" you've to return "{"provider": "kamino", "operation": "lend", "currency': "usdc", "amount": 100}"
"""
}


SOCIAL_EXTRACT_TEMPLATE = {
    "system": """Just answer the question"""
}

blockchain_extract_template = ChatPromptTemplate.from_messages(
    [
        ("system", BLOCKCHAIN_EXTRACT_TEMPLATE['system']),
        ("human", "{query}"),
    ]
)


social_extract_template = ChatPromptTemplate.from_messages(
    [
        ("system", SOCIAL_EXTRACT_TEMPLATE['system']),
        ("human", "{query}"),
    ]
)
