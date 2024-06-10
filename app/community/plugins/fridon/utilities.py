from app.community.helpers.chains import create_retriever_chain
from app.core.plugins.utilities import BaseUtility


class FridonRagUtility(BaseUtility):
    async def arun(self, question: str, *args, **kwargs) -> str:
        retrieval_chain = create_retriever_chain("app/community/plugins/fridon/fridon.md")
        response = await retrieval_chain.ainvoke({"input": question})

        return response

