from app.core.plugins.utilities import BlockchainUtility

class JupyterSwapUtility(BlockchainUtility):
    name = "jupyter-swap"
    description = "A utility that allows you to exchange one token to another using jupyter"

    async def run(
            self,
            from_token: str,
            to_token: str,
            amount: int,
            *args,
            **kwargs
    ) -> dict:
        request = {
            "plugin": "wallet",
            "function": "transfer",
            "args": {
                "fromToken": from_token,
                "toToken": to_token,
                "amount": amount,
            }
        }
        return request
