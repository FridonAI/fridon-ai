import json
from abc import ABC, abstractmethod
from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel

from app.adapters.blockchain import get_transfer_tx, get_stake_borrow_lend_tx, get_balance
from app.adapters.discord import get_available_servers


class Adapter(ABC, BaseModel):
    @abstractmethod
    async def get_response(self, chat_id, wallet_id):
        pass


class DefiStakeBorrowLendAdapter(Adapter):
    operation: Literal["stake", "borrow", "supply", "unstake", "stake", "withdraw", "repay"] | None
    provider: Literal["kamino"] | None
    currency: str | None
    amount: float | None
    status: bool
    comment: str | None

    async def get_response(self, chat_id, wallet_id):
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


class DefiBalanceAdapter(Adapter):
    status: bool
    comment: str | None
    provider: Literal["kamino", "wallet"] | None
    operation: Literal["all", "supply", "borrow"] | None
    currency: str | None

    async def get_response(self, chat_id, wallet_id):
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

    async def get_response(self, chat_id, wallet_id):
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

    async def get_response(self, chat_id, wallet_id):
        return self.message

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTalkerAdapter)


class CoinSearcherAdapter(Adapter):
    message: str

    async def get_response(self, chat_id, wallet_id):
        return self.message

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTalkerAdapter)


class DiscordActionAdapter(Adapter):
    status: bool
    comment: str | None
    action: Literal["follow", "unfollow"] | None
    server: str | None

    async def get_response(self, chat_id, wallet_id):
        return self.comment

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTalkerAdapter)

    @staticmethod
    def input_formatter():
        servers = get_available_servers()
        return {
            "query": lambda x: x["query"],
            "servers_list": servers,
        }





