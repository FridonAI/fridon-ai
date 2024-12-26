from pydantic import BaseModel, Field

from fridonai_core.plugins.utilities.llm import LLMUtility


class DatetimeExtractorUtility(LLMUtility):
    class StartEndDatetimeOutput(BaseModel):
        """Datetime string with iso format, it's allowed to be both or one None"""

        start_time: str | None = None
        end_time: str | None = None

    llm_job_description: str = """You are a starting and ending datetime extractor from user's input to the chat assistant. \
Return datetime in iso format like: 2022-01-01 12:00:00. 
There can be only starting_time, only ending_time, both, or none of them.
REMEMBER if there is no starting or ending time mentioned use None for that.
User input: {user_input}
"""
    structured_output: type = StartEndDatetimeOutput

    async def _arun(self, user_input: str, *args, **kwargs) -> dict:
        return {
            "user_input": user_input,
        }
