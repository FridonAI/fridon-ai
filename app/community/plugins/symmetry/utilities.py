from app.core.plugins.utilities import RemoteUtility


class SymmetryBalanceUtility(RemoteUtility):
    async def _arun(self, *args, wallet_id: str, **kwargs) -> dict:
        request = {
            "plugin": "symmetry",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            }
        }

        return request
