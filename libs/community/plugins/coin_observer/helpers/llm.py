from fridonai_core.graph.models import get_model
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field


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


def get_response_generator_chain() -> ChatPromptTemplate:
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
        You are generating notification messages.""",
            ),
            (
                "human",
                """
                Given the coin:

                {coin}

                Given the filter:

                {filter}

                Given the following indicators:

                {indicators}

                Generate a notification message based on the filter. Give the user information that the filter has been triggered.
                """,
            ),
        ]
    )

    return prompt | llm | StrOutputParser()
