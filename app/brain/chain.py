from langchain.utils.math import cosine_similarity
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.brain.templates import blockchain_extract_template, social_extract_template

embeddings = OpenAIEmbeddings()

flow_categories = ['blockchain', 'social-networks']
flow_category_embeddings = embeddings.embed_documents(flow_categories)

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)


blockchain_chain = (
    blockchain_extract_template
    | llm
)

social_chain = (
    social_extract_template
    | llm
)


def prompt_router(input):
    query_embedding = embeddings.embed_query(input["query"])
    similarity = cosine_similarity([query_embedding], flow_category_embeddings)[0]
    most_similar = flow_categories[similarity.argmax()]
    print("Using blockchain" if most_similar == 'blockchain' else "Using social networks")
    return most_similar


branch = RunnableBranch(
    (lambda x: x['category'] == 'blockchain', blockchain_chain),
    (lambda x: x['category'] == 'social', social_chain),
    blockchain_chain,
)

full_chain = {"query": lambda x: x["query"], "category": RunnableLambda(prompt_router)} | branch


def generate_response(query):
    response = full_chain.invoke({'query': query})
    return response.content
