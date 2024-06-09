from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.plugins.utilities import BaseUtility
from app.settings import settings

retriever = None
def get_retriever():
    global retriever

    if retriever:
        return retriever

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=0
    )
    loader = TextLoader("app/community/plugins/fridon/fridon.md")
    documents = loader.load()

    docs = text_splitter.split_documents(documents)
    db = FAISS.from_documents(docs, OpenAIEmbeddings(model="text-embedding-3-small"))
    retriever = db.as_retriever()
    return retriever


class FridonRagUtility(BaseUtility):
    async def arun(self, question: str, *args, **kwargs) -> str:
        retrieval_qa_prompt = PromptTemplate.from_template("""\
Answer any use questions based solely on the context below:
<context>
{context}
</context>

human: {input}""")
        llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY, verbose=True)
        combine_docs_chain = create_stuff_documents_chain(
            llm, retrieval_qa_prompt
        )
        retrieval_chain = create_retrieval_chain(get_retriever(), combine_docs_chain)

        response = await retrieval_chain.ainvoke({"input": question})

        return response



