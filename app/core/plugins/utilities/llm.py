import json
import os
from typing import Any

import aiohttp
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic.v1 import Field

from app.core.plugins.utilities.base import BaseUtility
from app.settings import settings


class LLMUtility(BaseUtility):
    llm_job_description: str = Field(description="Explicit description of the llm what it should do.")

    async def arun(self, *args, **kwargs) -> dict | str | Any:
        placeholders = await self._arun(*args, **kwargs)

        prompt = PromptTemplate.from_template(self.llm_job_description)
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY, verbose=True)

        chain = prompt | llm | StrOutputParser()

        result = await chain.ainvoke(placeholders)

        return result
