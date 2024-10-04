from fridonai_core.plugins.utilities.mock import BlockchainMockUtility


class JupiterSwapMockUtility(BlockchainMockUtility):
    async def arun(
        self,
        from_token: str,
        to_token: str,
        amount: float | int,
        *args,
        wallet_id: str = "Wallet007007",
        **kwargs,
    ) -> str:
        return f"Successfully swapped {amount} {from_token} to {to_token} from wallet {wallet_id}."
