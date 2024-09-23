from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from settings import settings

prompt = PromptTemplate.from_template("""\
You are expert in assessing user's chat with assistant. You have to assign score to user's current message from 0 to 2.\

Past several messages of user and assistant response on the last message are given.

There are several things to take into account:

1. If user is abusing the chat the score should be near to 0. You have to use last messages for this.
2. More diverse user's messages higher score should be.
3. If assistant message says that user's request couldn't be done, you should assign score to 0.


<user_past_messages>
{past_messages}
</user_past_messages>

<user_current_message>
{user_message}
</user_current_message>

<assistant_response>
{assistant_response}
</assistant_response>

""")

class ScoreOutput(BaseModel):
    "What score should be assigned to user's message"
    score: float | int = Field(description="Score from 0 to 2")

llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY, verbose=True)

class ScorerChain(BaseModel):
    structured_output: type[BaseModel] = ScoreOutput
    prompt: PromptTemplate = prompt

    @property
    def _chain(self) -> Runnable:
        return prompt | llm.with_structured_output(self.structured_output)

    async def arun(self, user_message, past_messages, response):
        return (await self._chain.ainvoke(
            {
                "past_messages": past_messages,
                "user_message": user_message,
                "assistant_response": response
            }
        )).score

    class Config:
        arbitrary_types_allowed = True
