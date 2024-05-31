from app.core.utilities import BlockchainUtility, RemoteUtility
from app.core.utils import blockchain, remote


class KaminoBorrowLendUtility(BlockchainUtility):
    name = "kamino-borrow-lend"
    description = "A utility that allows you to borrow and lend tokens on Kamino"

    @blockchain
    async def run(
            self,
            operation: str,
            currency: str,
            amount: int,
            **kwargs
    ) -> dict:
        request = {
            "plugin": "kamino",
            "function": "borrowlend",
            "args": {
                "operation": operation,
                "currency": currency,
                "amount": amount,
            }
        }
        return request


class KaminoBalanceUtility(RemoteUtility):
    name = "kamino-balance"
    description = "A utility that allows you to get your Kamino balance"

    @remote
    async def run(self, /, config: dict) -> dict:
        request = {
            "plugin": "kamino",
            "function": "balance",
        }

        return request
