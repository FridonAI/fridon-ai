from fridonai_core.plugins.utilities import BlockchainUtility, RemoteUtility


class WalletTransferUtility(BlockchainUtility):
    async def _arun(
        self,
        currency: str,
        amount: float | int,
        to_wallet_address: str,
        wallet_id: str,
        *args,
        **kwargs,
    ) -> dict:
        request = {
            "plugin": "wallet",
            "function": "transfer",
            "args": {
                "currency": currency,
                "amount": amount,
                "toAddress": to_wallet_address,
                "walletAddress": wallet_id,
            },
        }
        return request


class WalletBalanceUtility(RemoteUtility):
    async def _arun(
        self, *args, currency: str | None = None, wallet_id, **kwargs
    ) -> dict:
        request = {
            "plugin": "wallet",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            },
        }

        if currency is not None:
            request["args"]["currency"] = currency

        return request
