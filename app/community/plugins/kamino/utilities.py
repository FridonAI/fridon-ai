from app.core.plugins.utilities import BlockchainUtility, RemoteUtility


class KaminoBorrowLendUtility(BlockchainUtility):
    name = "kamino-borrow-lend"
    description = "A utility that allows you to borrow and lend tokens on Kamino"

    async def _arun(
            self,
            operation: str,
            currency: str,
            amount: int,
            *args,
            wallet_id: str,
            **kwargs
    ) -> dict:
        request = {
            "plugin": "kamino",
            "function": "borrowlend",
            "args": {
                "walletAddress": wallet_id,
                "operation": operation,
                "currency": currency,
                "amount": amount,
            }
        }
        return request


class KaminoBalanceUtility(RemoteUtility):
    name = "kamino-balance"
    description = "A utility that allows you to get your Kamino balance"

    async def _arun(self, *args, wallet_id: str, **kwargs) -> dict:
        request = {
            "plugin": "kamino",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            }
        }

        return request
