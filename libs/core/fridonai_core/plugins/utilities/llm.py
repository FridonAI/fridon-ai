from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from fridonai_core.plugins.utilities.base import BaseUtility
from settings import settings


class LLMUtility(BaseUtility):
    llm_job_description: str = Field(
        description="Explicit description of the llm what it should do."
    )
    structured_output: type[BaseModel] | None = None

    async def arun(self, *args, **kwargs) -> BaseModel | dict | str | Any:
        placeholders = await self._arun(*args, **kwargs)

        prompt = PromptTemplate.from_template(self.llm_job_description)
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            verbose=True,
        )

        if self.structured_output is not None:
            llm = llm.with_structured_output(self.structured_output)
            chain = prompt | llm | StrOutputParser()
        else:
            chain = prompt | llm

        result = await chain.ainvoke(placeholders)

        return result
