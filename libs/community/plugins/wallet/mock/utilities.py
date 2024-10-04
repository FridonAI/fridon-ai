from fridonai_core.plugins.utilities.mock import BlockchainMockUtility, RemoteMockUtility


class WalletTransferMockUtility(BlockchainMockUtility):
    async def arun(
        self,
        currency: str,
        amount: float | int,
        to_wallet_address: str,
        wallet_id: str = "Wallet007007",
        *args,
        **kwargs,
    ) -> str:
        return f"{amount} {currency} successfully transferred from {wallet_id} to {to_wallet_address}"


class WalletBalanceMockUtility(RemoteMockUtility):
    wallet_balances = {
        "sol": 23,
        "eth": 1.2,
    }

    async def arun(
        self,
        *args,
        currency: str | None = None,
        wallet_id: str = "Wallet007007",
        **kwargs,
    ) -> dict:
        if currency is None:
            return {"data": self.wallet_balances}
        amount = self.wallet_balances.get(currency, 0)
        return {"data": {currency: amount}}
