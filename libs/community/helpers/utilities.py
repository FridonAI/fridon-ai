from pydantic import BaseModel, Field

from fridonai_core.plugins.utilities.llm import LLMUtility


class DatetimeExtractorUtility(LLMUtility):
    class DatetimeExtractorOutput(BaseModel):
        """Datetime string with iso format"""

        starting_time: str | None = Field(
            default=None,
            description="Valid iso format datetime which is starting time of a period",
        )
        ending_time: str | None = Field(
            default=None,
            description="Valid iso format datetime which is ending time of a period",
        )

    llm_job_description: str = """You are a starting and ending datetime extractor from user's input to the chat assistant. \
Return datetime in iso format like: 2022-01-01 12:00:00"
User input: {user_input}
"""
    structured_output: type = DatetimeExtractorOutput

    async def _arun(self, user_input: str, *args, **kwargs) -> dict:
        return {
            "user_input": user_input,
        }
