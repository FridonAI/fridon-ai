from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from settings import settings

default_retriever_prompt_template = """\
Answer any use questions based solely on the context below:
<context>
{context}
</context>

human: {input}"""


def get_retriever(document_path):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    loader = TextLoader(document_path)
    documents = loader.load()

    docs = text_splitter.split_documents(documents)
    db = FAISS.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))
    retriever = db.as_retriever()
    return retriever


def create_retriever_chain(
    docs_path, prompt_template=default_retriever_prompt_template
):
    retrieval_qa_prompt = PromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
        verbose=True,
    )
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_prompt)
    retriever = get_retriever(docs_path)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    return retrieval_chain
