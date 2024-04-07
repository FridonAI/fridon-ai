import json

from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


retriever = None


def get_coins_retriever():
    global retriever

    if retriever:
        return retriever

    loader = JSONLoader(
        file_path='./data/coin-description.json',
        jq_schema='.[]',
        text_content=False
    )

    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(texts, embeddings)

    retriever = db.as_retriever()

    return retriever


def get_coin_description(coin):
    if coin is None:
        return ""
    with open('./data/coin-description.json') as f:
        data = json.load(f)
        for coin_name, desc in data.items():
            if coin_name.lower() == coin.lower():
                return desc

    return ""


def get_media_retriever(whole_text):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(whole_text)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_texts(texts, embeddings)

    retriever = db.as_retriever()

    return retriever



