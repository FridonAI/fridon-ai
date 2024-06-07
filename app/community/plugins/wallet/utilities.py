from app.core.plugins.utilities import BlockchainUtility, RemoteUtility


class WalletTransferUtility(BlockchainUtility):
    name = "wallet-transfer"
    description = "A utility that allows you to transfer tokens to another wallet"

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
    name = "wallet-balance"
    description = "A utility that allows you to get your wallet balances"

    async def _arun(self, *args, wallet_id, **kwargs) -> dict:
        request = {
            "plugin": "wallet",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            }
        }

        return request
