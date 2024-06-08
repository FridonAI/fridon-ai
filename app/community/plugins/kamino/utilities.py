from app.core.plugins.utilities import BlockchainUtility, RemoteUtility


class KaminoBorrowLendUtility(BlockchainUtility):
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

    async def _arun(self, *args, wallet_id: str, **kwargs) -> dict:
        request = {
            "plugin": "kamino",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            }
        }

        return request
