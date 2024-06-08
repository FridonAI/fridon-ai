from app.core.plugins.utilities import BlockchainUtility, RemoteUtility


class WalletTransferUtility(BlockchainUtility):
    async def _arun(
            self,
            currency: str,
            amount: int,
            to_wallet_address: str,
            wallet_id: str,
            *args,
            **kwargs
    ) -> dict:
        request = {
            "plugin": "wallet",
            "function": "transfer",
            "args": {
                "currency": currency,
                "amount": amount,
                "toAddress": to_wallet_address,
                "walletAddress": wallet_id,
            }
        }
        return request


class WalletBalanceUtility(RemoteUtility):
    async def _arun(self, *args, wallet_id, **kwargs) -> dict:
        request = {
            "plugin": "wallet",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            }
        }

        return request
