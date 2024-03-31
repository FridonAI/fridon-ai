from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


def get_coins_retriever():
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

    coins_retriever = db.as_retriever()
    return coins_retriever


def get_media_retriever(whole_text):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_text(whole_text)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_texts(texts, embeddings)

    retriever = db.as_retriever()

    return retriever



