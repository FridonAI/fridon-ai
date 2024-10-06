from typing import Literal

import polars as pl
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from settings import settings


class BulishIndicator(BaseModel):
    """Tag for bulish / bearish coin based on coin technicals."""

    symbol: str = Field(description="Symbol of the coin")
    tag: Literal["strong bulish", "bullish", "neutral", "bearish", "strong bearish"] = (
        Field(description="Tag for the coin")
    )
    reason: str = Field(description="Short reason for the tag")


def get_bulish_indicator_chain() -> ChatPromptTemplate:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
        verbose=True,
    )

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


async def calculate_bulish_indicator(df: pl.DataFrame) -> pl.DataFrame:
    chain = get_bulish_indicator_chain()

    # Select 'coin' as symbol and all other columns for last_day_summary
    inputs = df.select(
        pl.col("coin").alias("symbol"),
        pl.struct(pl.exclude("coin")).alias("last_day_summary"),
    ).to_dicts()

    # Convert struct to string representation for each row
    inputs = [
        {
            "symbol": row["symbol"],
            "last_day_summary": "\n".join(
                f"{k}: {v}" for k, v in row["last_day_summary"].items()
            ),
        }
        for row in inputs
    ]

    bulish_indicators = await chain.abatch(inputs)
    bulish_indicator_data = [
        {"coin": indicator.symbol, "tag": indicator.tag, "reason": indicator.reason}
        for indicator in bulish_indicators
    ]

    bulish_df = pl.DataFrame(bulish_indicator_data)

    return df.select("coin", "timestamp").join(
        bulish_df, on="coin", how="left"
    )
