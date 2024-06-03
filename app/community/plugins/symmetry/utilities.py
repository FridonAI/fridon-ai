from app.core.utilities import RemoteUtility
from app.core.utils import remote


class SymmetryBalanceUtility(RemoteUtility):
    name = "symmetry-balance"
    description = "A utility that allows you to get balances from Symmetry"

    @remote
    async def run(self, *args, **kwargs) -> dict:
        request = {
            "plugin": "symmetry",
            "function": "balance",
        }

        return request
