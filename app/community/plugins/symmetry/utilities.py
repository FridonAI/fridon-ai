from app.core.plugins.utilities import RemoteUtility


class SymmetryBalanceUtility(RemoteUtility):
    name = "symmetry-balance"
    description = "A utility that allows you to get balances from Symmetry"

    async def run(self, *args, wallet_id: str, **kwargs) -> dict:
        request = {
            "plugin": "symmetry",
            "function": "balance",
            "args": {
                "walletAddress": wallet_id,
            }
        }

        return request
