from pydantic import BaseModel
from fridonai_core.plugins.utilities.llm import LLMUtility
from fridonai_core.plugins.schemas import BaseToolInput
from fridonai_core.plugins.tools import BaseTool


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


class DatetimeExtractorToolInput(BaseToolInput):
    user_input: str


DatetimeExtractorTool = BaseTool(
    name="datetime-extractor",
    description="Helper tool to extract starting and ending times of a period from user input. Use only when user mentions date and extraction is needed.",
    args_schema=DatetimeExtractorToolInput,
    utility=DatetimeExtractorUtility(),
)
