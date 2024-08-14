from app.core.plugins.utilities.mock import BlockchainMockUtility, RemoteMockUtility


class WalletTransferMockUtility(BlockchainMockUtility):
    async def arun(
            self,
            currency: str,
            amount: float | int,
            to_wallet_address: str,
            wallet_id: str = "Wallet007007",
            *args,
            **kwargs
    ) -> str:
        return f"{amount} {currency} successfully transfered from {wallet_id} to {to_wallet_address}"


class WalletBalanceMockUtility(RemoteMockUtility):
    async def arun(
            self,
            *args,
            currency: str | None = None,
            wallet_id: str = "Wallet007007",
            **kwargs
    ) -> dict:
        return {"data": {"sol": 23}}


