from app.core.plugins.utilities import RemoteUtility


class SymmetryBalanceUtility(RemoteUtility):
    name = "symmetry-balance"
    description = "A utility that allows you to get balances from Symmetry"

    async def run(self, *args, **kwargs) -> dict:
        request = {
            "plugin": "symmetry",
            "function": "balance",
        }

        return request
