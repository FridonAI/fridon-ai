from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from pydantic.v1 import BaseModel


class DefiStakeBorrowLendParameters(BaseModel):
    operator: Literal["stake", "borrow", "lend", "unstake", "stake", "withdraw", "repay"] | None
    provider: Literal["kamino", "marginify", "pyth-governance", "jup-governance"] | None
    currency: str | None
    amount: float | None
    status: bool
    comment: str | None

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiStakeBorrowLendParameters)


class DefiBalanceParameters(BaseModel):
    provider: Literal["kamino", "marginify", "pyth-governance", "jup-governance", "all", None]
    operation: Literal["walletbalance", "lend", "borrow", "stake", None]
    currency: str | None

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiBalanceParameters)


class DefiTransferParameters(BaseModel):
    status: bool
    comment: str | None
    currency: str | None
    wallet: str | None

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTransferParameters)


class DefiTalkerParameters(BaseModel):
    message: str

    @staticmethod
    def parser() -> PydanticOutputParser:
        return PydanticOutputParser(pydantic_object=DefiTalkerParameters)
