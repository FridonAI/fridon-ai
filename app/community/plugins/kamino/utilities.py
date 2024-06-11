from typing import Literal

from app.core.plugins.utilities import BlockchainUtility, RemoteUtility


class KaminoBorrowLendUtility(BlockchainUtility):
    async def _arun(
            self,
            operation: Literal['borrow', 'supply', 'repay', 'withdraw'],
            currency: str,
            amount: float | int,
            *args,
            wallet_id: str,
            **kwargs
    ) -> dict:
        request = {
            "plugin": "kamino",
            "function": operation,
            "args": {
                "walletAddress": wallet_id,
                "operation": operation,
                "currency": currency,
                "amount": amount,
            }
        }
        return request


class KaminoBalanceUtility(RemoteUtility):

    async def _arun(
            self,
            *args,
            wallet_id: str,
            operation: str | None = None,
            currency: str | None = None,
            **kwargs
    ) -> dict:
        request = {
            "plugin": "kamino",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            }
        }

        if operation is not None:
            request["args"]["operation"] = operation
        if currency is not None:
            request["args"]["currency"] = currency

        return request
