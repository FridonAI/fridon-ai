from fridonai_core.plugins.utilities import BlockchainUtility


class JupiterSwapUtility(BlockchainUtility):
    async def _arun(
        self,
        from_token: str,
        to_token: str,
        amount: float | int,
        *args,
        wallet_id: str,
        **kwargs,
    ) -> dict:
        request = {
            "plugin": "jupiter",
            "function": "swap",
            "args": {
                "fromToken": from_token,
                "toToken": to_token,
                "amount": amount,
                "walletAddress": wallet_id,
            },
        }
        return request
