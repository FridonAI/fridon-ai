from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.plugins.utilities import BaseUtility
from app.settings import settings


def get_retriever():
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=0
    )
    with open('app/community/plugins/fridon/fridon.md', 'r') as f:
        policy = f.read()

    policy_splits = text_splitter.split_text(policy)
    vectorstore = Chroma.from_texts(policy_splits, collection_name="policy_rag", embedding=OpenAIEmbeddings(model="text-embedding-3-small"))
    return vectorstore.as_retriever()


retriever = get_retriever()


class FridonRagUtility(BaseUtility):
    async def arun(self, question: str, *args, **kwargs) -> str:
        retrieval_qa_prompt = PromptTemplate.from_template("""\
Answer any use questions based solely on the context below:
<context>
{context}
</context>

human: {input}""")
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY, verbose=True)
        combine_docs_chain = create_stuff_documents_chain(
            llm, retrieval_qa_prompt
        )
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

        response = await retrieval_chain.ainvoke({"input": question})

        return response



