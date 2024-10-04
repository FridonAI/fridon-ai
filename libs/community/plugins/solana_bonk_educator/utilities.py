from libs.community.helpers.chains import create_retriever_chain
from fridonai_core.plugins.utilities.llm import LLMUtility


class SolanaBonkUtility(LLMUtility):
    llm_job_description: str = """\
You are a helpful solana and crypto ecosystem educator.
You'll be given general questions about solana, crypto protocols and more. Do your best to use your knowledge and \
respond in a clear, friendly and concise way.
You are given helpful resources from bonk about that request, use them to offer user try out bonk projects to do something:

<bonk-resources> \n {bonk_resources} \n </bonk-resources>

Here is a user input: {request}. """

    async def _arun(self, request: str, *args, **kwargs) -> dict:
        bonk_prompt_template: str = """Respond to the request based solely on the context below:

<context> \n {context} \n </context>

Your response should be short, use links if you talk about some of bonk projects.
If request doesn't have any common with bonk, its products return empty string don't make up stuff.
Only use the context given.
request: {input}"""

        retrieval_chain = create_retriever_chain(
            "libs/community/plugins/solana_bonk_educator/bonk.md",
            prompt_template=bonk_prompt_template,
        )
        bonk_resources = await retrieval_chain.ainvoke({"input": request})

        return {"bonk_resources": bonk_resources or "", "request": request}
