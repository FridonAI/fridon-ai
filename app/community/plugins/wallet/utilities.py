from app.core.utilities import BlockchainUtility, RemoteUtility
from app.core.utils import blockchain, remote


class WalletTransferUtility(BlockchainUtility):
    name = "wallet-transfer"
    description = "A utility that allows you to transfer tokens to another wallet"

    @blockchain
    async def run(
            self,
            currency: str,
            amount: int,
            to_wallet_address: str,
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
            }
        }
        return request


class WalletBalanceUtility(RemoteUtility):
    name = "wallet-balance"
    description = "A utility that allows you to get your wallet balances"

    @remote
    async def run(self, *args, **kwargs) -> dict:
        request = {
            "plugin": "wallet",
            "function": "balance",
        }

        return request
