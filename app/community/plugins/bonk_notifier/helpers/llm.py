from typing import Literal

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field

from app.settings import settings


class BulishIndicator(BaseModel):
    """Tag for bulish / bearish coin based on coin technicals."""

    symbol: str = Field(description="Symbol of the coin")
    tag: Literal["strong bulish", "bullish", "neutral", "bearish", "strong bearish"] = Field(description="Tag for the coin")
    reason: str = Field(description="Short reason for the tag")


def get_bulish_indicator_chain() -> ChatPromptTemplate:
    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY, verbose=True)

    check_propmt = ChatPromptTemplate.from_messages([
        ("system", """Assume the role as a leading Technical Analysis (TA) expert in the stock market, \
    a modern counterpart to Charles Dow, John Bollinger, and Alan Andrews. \
    Your mastery encompasses both stock fundamentals and intricate technical indicators. \
    You possess the ability to decode complex market dynamics, \
    providing clear insights and recommendations backed by a thorough understanding of interrelated factors."""),
        ("human", """Given Technical Analysis for {symbol} on the last trading day. \
    Tag the coin with one  of signals ["strong bulish", "bullish", "neutral", "bearish", "strong bearish"]"""),
        ("human", "Summary of Technical Indicators for the Last Day: \n\n {last_day_summary}"),

    ])

    return check_propmt | llm.with_structured_output(BulishIndicator)


async def generate_bonk_tag(bonk_summary: dict) -> dict:
    chain = get_bulish_indicator_chain()
    bonk_tag = await chain.ainvoke(bonk_summary)
    return bonk_tag.dict()


def get_bonk_bullish_notification_chain() -> ChatPromptTemplate:
    llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY, verbose=True)

    check_propmt = ChatPromptTemplate.from_messages([
        ("system", """You are expert in generating notifications for bullish coins."""),
        ("human", """Given the metadata of notification generate notification as short text, maximum 3 sentences."""),
        ("human", "Notification: \n\n {description}"),
    ])

    return check_propmt | llm | StrOutputParser()


async def generate_bonk_bullish_notification(bonk_tag: dict) -> dict:
    chain = get_bonk_bullish_notification_chain()
    bonk_notification = await chain.ainvoke({"description": bonk_tag})
    return bonk_notification
