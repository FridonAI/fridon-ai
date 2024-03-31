import asyncio

from langchain_community.chat_message_histories.postgres import PostgresChatMessageHistory
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from app.brain.memory import get_chat_history
from app.brain.retriever import get_coins_retriever
from app.brain.schema import (
    DefiStakeBorrowLendAdapter, DefiTransferAdapter, DefiBalanceAdapter, DefiTalkerAdapter,
    CoinSearcherAdapter, DiscordActionAdapter, CoinChartSimilarityAdapter, MediaQueryExtractAdapter,
)
from app.brain.templates import get_prompt


def get_defi_stake_borrow_lend_extract_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('defi_stake_borrow_lend_extract', personality)
    return (
        prompt
        | llm
        | DefiStakeBorrowLendAdapter.parser()
    )


def get_defi_balance_extract_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('defi_balance_extract', personality)
    return (
        prompt
        | llm
        | DefiBalanceAdapter.parser()
    )


def get_defi_transfer_extract_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('defi_transfer_extract', personality)
    return (
        prompt
        | llm
        | DefiTransferAdapter.parser()
    )


def get_discord_action_extract_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('discord_action_extract', personality)
    return (
        RunnableLambda(DiscordActionAdapter.input_formatter)
        | prompt
        | llm
        | DiscordActionAdapter.parser()
    )


def get_coin_chart_similarity_extract_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('coin_chart_similarity_extract', personality)
    return (
        RunnableLambda(DiscordActionAdapter.input_formatter)
        | prompt
        | llm
        | CoinChartSimilarityAdapter.parser()
    )


def get_media_query_extract(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('media_query_extract', personality)
    return (
        RunnableLambda(MediaQueryExtractAdapter.input_formatter)
        | prompt
        | llm
        | MediaQueryExtractAdapter.parser()
    )


def get_defi_talker_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('defi_talker', personality)
    return RunnableWithMessageHistory(
        (
            prompt
            | llm
            | DefiTalkerAdapter.parser()
        ),
        get_chat_history,
        input_messages_key="query",
        history_messages_key="history",
    )


def get_coin_search_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('coin_search', personality)
    return RunnableWithMessageHistory(
        (
            {
                "query": lambda x: x["query"],
                "context": RunnableLambda(lambda x: x["query"]) | get_coins_retriever(),
                "history": lambda x: x["history"]
            }
            | prompt
            | llm
            | CoinSearcherAdapter.parser()
        ),
        get_chat_history,
        input_messages_key="query",
        history_messages_key="history",
    )


def get_media_talker_chain(
        personality,
        retriever,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('media_talker', personality)
    return RunnableWithMessageHistory(
        (
            {
                "query": lambda x: x["query"],
                "context": RunnableLambda(lambda x: x["query"]) | retriever,
                "history": lambda x: x["history"]
            }
            | prompt
            | llm
            | StrOutputParser()
        ),
        get_chat_history,
        input_messages_key="query",
        history_messages_key="history"
    )


def get_error_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('error', personality)
    return (
        prompt
        | llm
        | StrOutputParser()
    )


def get_off_topic_chain(
        personality,
        llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
):
    prompt = get_prompt('off_topic', personality)
    return (
        prompt
        | llm
        | StrOutputParser()
    )


def get_chain(category, personality):
    match category:
        case "DefiStakeBorrowLend":
            return get_defi_stake_borrow_lend_extract_chain(personality)
        case "DeFiBalance":
            return get_defi_balance_extract_chain(personality)
        case "DeFiTransfer":
            return get_defi_transfer_extract_chain(personality)
        case "CoinSearch":
            return get_coin_search_chain(personality)
        case "DiscordAction":
            return get_discord_action_extract_chain(personality)
        case "CoinChartSimilarity":
            return get_coin_chart_similarity_extract_chain(personality)
        case "DeFiTalker":
            return get_defi_talker_chain(personality)
        case "MediaTalker":
            return get_media_query_extract(personality)

    return get_off_topic_chain(personality)

