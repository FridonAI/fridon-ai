from typing import Literal

from app.core.plugins.utilities.mock import BlockchainMockUtility, RemoteMockUtility

class KaminoBorrowLendMockUtility(BlockchainMockUtility):
    async def arun(
            self,
            operation: Literal['borrow', 'supply', 'repay', 'withdraw'],
            currency: str,
            amount: float | int,
            *args,
            wallet_id: str = "Wallet007007",
            **kwargs
    ) -> str:
        return f"{operation.capitalize()} of {amount} {currency} was successful for wallet {wallet_id}."

class KaminoBalanceMockUtility(RemoteMockUtility):
    balances = {
        "borrow": {"sol": 5},
        "supply": {"usdc": 1000},
    }

    async def arun(
            self,
            *args,
            wallet_id: str = "Wallet007007",
            operation: str | None = None,
            currency: str | None = None,
            **kwargs
    ) -> dict:
        if operation and currency:
            amount = self.balances.get(operation, {}).get(currency, 0)
            return {"data": {operation: {currency: amount}}}
        elif operation:
            return {"data": {operation: self.balances.get(operation, {})}}
        elif currency:
            amounts = {op: data.get(currency, 0) for op, data in self.balances.items()}
            return {"data": {currency: amounts}}
        else:
            return {"data": self.balances}
