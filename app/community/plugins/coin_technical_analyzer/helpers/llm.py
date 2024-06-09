from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field

from app.settings import settings


class FilterResponse(BaseModel):
        """Binary score for satisfaction check on Technical Analysis."""

        symbol: str = Field(description="Symbol of the coin")
        binary_score: str = Field(description="Whether the user's filter satisfies the TA or not, 'yes' or 'no'")
        reason: str = Field(description="Short reason for the score")

def get_filter_chain() -> ChatPromptTemplate:
    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY, verbose=True)

    check_propmt = ChatPromptTemplate.from_messages([
        ("system", """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
    a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
    Your mastery encompasses both stock fundamentals and intricate technical indicators. \
    You possess the ability to decode complex market dynamics, \
    providing clear insights and recommendations backed by a thorough understanding of interrelated factors."""),
        ("human", """Given Technical Analysis for {symbol} on the last trading day. \
    Check if users query satisfies the TA."""),
        ("human", "Summary of Technical Indicators for the Last Day: \n\n {last_day_summary} \n\n  User's filter: {filter}"),

    ])

    return check_propmt | llm.with_structured_output(FilterResponse)
