from pydantic.v1 import BaseModel, Field

from app.core.plugins.utilities.llm import LLMUtility


class DatetimeExtractorUtility(LLMUtility):
    class DatetimeExtractorOutput(BaseModel):
        """Datetime string with iso format"""
        datetime: str = Field(description="Valid iso format datetime")

    llm_job_description = """You are a datetime extractor from user's input to the chat assistant. \
Return datetime in iso format like: 2022-01-01"
User input: {user_input}
"""
    structured_output = DatetimeExtractorOutput

    async def _arun(
            self,
            user_input: str,
            *args,
            **kwargs
    ) -> dict:
        return {
            "user_input": user_input,
        }
