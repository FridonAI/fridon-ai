from abc import ABC, abstractmethod
from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel

from app.adapters.blockchain import get_transfer_tx, get_stake_borrow_lend_tx


class Adapter(ABC, BaseModel):
    @abstractmethod
    async def get_response(self, chat_id, wallet_id):
        pass


class DefiStakeBorrowLendAdapter(Adapter):
    operator: Literal["stake", "borrow", "lend", "unstake", "stake", "withdraw", "repay"] | None
    provider: Literal["kamino", "marginify", "pyth-governance", "jup-governance"] | None
    currency: str | None
    amount: float | None
    status: bool
    comment: str | None

    async def get_response(self, chat_id, wallet_id):
        if None in [self.operator, self.provider, self.currency, self.amount]:
            return self.comment

        return await get_stake_borrow_lend_tx(
            self.provider,
            self.operator,
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
    provider: Literal["kamino", "marginify", "pyth-governance", "jup-governance", "all", None]
    operation: Literal["walletbalance", "lend", "borrow", "stake", None]
    currency: str | None

    async def get_response(self, chat_id, wallet_id):
        return "Your sol balance is: 10"

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

