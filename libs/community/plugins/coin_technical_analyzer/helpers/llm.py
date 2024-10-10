from typing import Literal

from fridonai_core.graph.models import get_model
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class FilterResponse(BaseModel):
    """Binary score for satisfaction check on Technical Analysis."""

    symbol: str = Field(description="Symbol of the coin")
    binary_score: str = Field(
        description="Whether the user's filter satisfies the TA or not, 'yes' or 'no'"
    )
    reason: str = Field(description="Short reason for the score")


def get_filter_chain() -> ChatPromptTemplate:
    llm = get_model()

    check_propmt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
    a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
    Your mastery encompasses both stock fundamentals and intricate technical indicators. \
    You possess the ability to decode complex market dynamics, \
    providing clear insights and recommendations backed by a thorough understanding of interrelated factors.""",
            ),
            (
                "human",
                """Given Technical Analysis for {symbol} on the last trading day. \
    Check if users query satisfies the TA.""",
            ),
            (
                "human",
                "Summary of Technical Indicators for the Last Day: \n\n {last_day_summary} \n\n  User's filter: {filter}",
            ),
        ]
    )

    return check_propmt | llm.with_structured_output(FilterResponse)


class BulishIndicator(BaseModel):
    """Tag for bulish / bearish coin based on coin technicals."""

    symbol: str = Field(description="Symbol of the coin")
    tag: Literal["strong bulish", "bullish", "neutral", "bearish", "strong bearish"] = (
        Field(description="Tag for the coin")
    )
    reason: str = Field(description="Short reason for the tag")


def get_bulish_indicator_chain() -> ChatPromptTemplate:
    llm = get_model()

    check_propmt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
    a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
    Your mastery encompasses both stock fundamentals and intricate technical indicators. \
    You possess the ability to decode complex market dynamics, \
    providing clear insights and recommendations backed by a thorough understanding of interrelated factors.""",
            ),
            (
                "human",
                """Given Technical Analysis for {symbol} on the last trading day. \
    Tag the coin with one  of signals ["strong bulish", "bullish", "neutral", "bearish", "strong bearish"]""",
            ),
            (
                "human",
                "Summary of Technical Indicators for the Last Day: \n\n {last_day_summary}",
            ),
        ]
    )

    return check_propmt | llm.with_structured_output(BulishIndicator)


async def generate_token_tags_list(token_summaries: list[dict]) -> list[dict]:
    chain = get_bulish_indicator_chain()

    results = []

    for i in range(0, len(token_summaries), 5):
        batch = token_summaries[i : i + 5]

        curr_results = await chain.abatch(batch)

        results.extend([x.dict() for x in curr_results])

    return results


class FilterGenerationResponse(BaseModel):
    filters: str = Field(..., description="The deltalake table filter expression.")


def get_filter_generator_chain() -> ChatPromptTemplate:
    llm = get_model()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
    a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
    Your mastery encompasses both stock fundamentals and intricate technical indicators. \
    You possess the ability to decode complex market dynamics, \
    providing clear insights and recommendations backed by a thorough understanding of interrelated factors. \
        You are generating filters for DeltaLake datasets based on the query.""",
            ),
            (
                "human",
                """
                Given the dataset schema:

                {schema}

                And the following query:

                {query}

                Generate a DeltaLake filter expression that can be used to filter the dataset based on the query.

                Use only pyarrow.compute when referencing specific columns with pc.field(...).

                Return only the filter expression of type pyarrow.compute.Expression.

                import pyarrow.compute as pc
                """,
            ),
        ]
    )

    return prompt | llm.with_structured_output(FilterGenerationResponse)
