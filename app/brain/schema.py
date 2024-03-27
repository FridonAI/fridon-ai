import json
from abc import ABC, abstractmethod
from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel

from app.adapters.blockchain import get_transfer_tx, get_stake_borrow_lend_tx, get_balance


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
        if None in [self.operation, self.provider, self.currency, self.amount]:
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
    operation: Literal["all", "supplied", "borrowed"] | None
    currency: str | None

    async def get_response(self, chat_id, wallet_id):
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
        if None in [self.amount,  self.currency]:
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

