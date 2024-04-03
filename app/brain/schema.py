import datetime
import json
from abc import ABC, abstractmethod
from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel

from app.adapters.blockchain import get_transfer_tx, get_stake_borrow_lend_tx, get_balance, get_points, get_swap_tx, get_symmetry_baskets
from app.adapters.coins import get_chart_similar_coins
from app.adapters.medias.discord import get_available_servers, follow_server, unfollow_server, \
    get_media_text, get_wallet_servers
from app.brain.memory import get_chat_history
from app.brain.retriever import get_media_retriever
from app.brain.templates import get_prompt
from app.settings import settings


class Adapter(ABC, BaseModel):
    @abstractmethod
    async def get_response(self, chat_id, wallet_id, personality):
        pass


class DefiStakeBorrowLendAdapter(Adapter):
    operation: Literal["stake", "borrow", "supply", "unstake", "stake", "withdraw", "repay"] | None
    provider: Literal["kamino"] | None
    currency: str | None
    amount: float | None
    status: bool
    comment: str | None

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        if not self.status:
            return self.comment

        return await get_stake_borrow_lend_tx(
            self.provider,
            self.operation,
            self.currency,
            self.amount,
            chat_id,
            wallet_id
        )

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiStakeBorrowLendAdapter)

class DefiSwapAdapter(Adapter):
    status: bool
    comment: str | None
    currency_from: str | None
    currency_to: str | None
    amount: float | None

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        if not self.status:
            return self.comment
        return await get_swap_tx(
            self.currency_from,
            self.currency_to,
            self.amount,
            chat_id,
            wallet_id
        )

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiSwapAdapter)
    
class DefiSymmetryBasketsAdapter(Adapter):
    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        symmetry_baskets = await get_symmetry_baskets()

        return json.dumps(symmetry_baskets)

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiSymmetryBasketsAdapter)

class DefiPointsAdapter(Adapter):
    provider: Literal["kamino", "symmetry", 'drift', 'all'] | None

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        points_response = await get_points(
            wallet_id,
            self.provider,
        )

        return json.dumps(points_response['data'])

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiPointsAdapter)

class DefiBalanceAdapter(Adapter):
    status: bool
    comment: str | None
    provider: Literal["kamino", "wallet", "symmetry", "all"] | None
    operation: Literal["all", "supply", "borrow"] | None
    currency: str | None

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        if not self.status:
            return self.comment
        balance_response = await get_balance(
            wallet_id,
            self.provider,
            self.operation,
            self.currency,
        )
        return json.dumps(balance_response['data'])

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiBalanceAdapter)


class DefiTransferAdapter(Adapter):
    status: bool
    comment: str | None
    currency: str | None
    amount: float | None
    wallet: str | None

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        if not self.status:
            return self.comment
        return await get_transfer_tx(
            self.wallet,
            self.currency,
            self.amount,
            chat_id,
            wallet_id
        )

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTransferAdapter)


class DefiTalkerAdapter(Adapter):
    message: str

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        return self.message

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTalkerAdapter)


class CoinSearcherAdapter(Adapter):
    message: str

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        return self.message

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTalkerAdapter)


class DiscordActionAdapter(Adapter):
    status: bool
    comment: str | None
    action: Literal["follow", "unfollow"] | None
    server: str | None

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        if not self.status:
            return self.comment

        if self.action == "follow":
            return await follow_server(self.server, wallet_id)
        elif self.action == "unfollow":
            return await unfollow_server(self.server, wallet_id)
        return "Unknown action received, nor follow or unfollow."

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DiscordActionAdapter)

    @staticmethod
    async def input_formatter(inp):
        servers = await get_available_servers()
        return {
            "query": inp["query"],
            "servers_list": servers,
        }


class CoinChartSimilarityAdapter(Adapter):
    status: bool
    comment: str | None = None
    coin: str | None = None
    start_date: str | None = None

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=CoinChartSimilarityAdapter)

    async def get_response(self, chat_id, wallet_id, *args, **kwargs):
        if not self.status:
            return self.comment

        response = get_chart_similar_coins(self.coin, self.start_date)
        return response


class MediaQueryExtractAdapter(Adapter):
    servers: list[str]
    days: int
    query: str

    async def get_response(self, chat_id, wallet_id, personality, *args, **kwargs):
        date = (datetime.date.today() - datetime.timedelta(days=self.days)).isoformat()
        whole_text = await get_media_text(self.servers, date)
        retriever = get_media_retriever(whole_text)

        def get_media_talker_chain(
                personality,
                retriever,
                llm=ChatOpenAI(model=settings.GPT_MODEL, temperature=0)
        ):
            prompt = get_prompt('media_talker', personality)
            return RunnableWithMessageHistory(
                (
                        {
                            "query": lambda x: x["query"],
                            "context": RunnableLambda(lambda x: x["query"]) | retriever,
                            "history": lambda x: x["history"],
                        }
                        | prompt
                        | llm
                        | StrOutputParser()
                ),
                get_chat_history,
                input_messages_key="query",
                history_messages_key="history"
            )

        chain = get_media_talker_chain(personality, retriever)

        response = await chain.ainvoke(
            {"query": self.query},
            config={"configurable": {"session_id": chat_id}}
        )
        return response

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=MediaQueryExtractAdapter)

    @staticmethod
    async def input_formatter(inp):
        servers = await get_wallet_servers(inp["wallet_id"])
        return {
            "query": inp["query"],
            "user_servers_list": servers,
        }
