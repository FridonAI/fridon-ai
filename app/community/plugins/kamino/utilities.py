from app.core.utilities import BlockchainUtility, RemoteUtility


class KaminoBorrowLendUtility(BlockchainUtility):
    name = "kamino-borrow-lend"
    description = "A utility that allows you to borrow and lend tokens on Kamino"

    async def run(self, operation: str, currency: str, amount: int, wallet_id: str, chat_id: str) -> str:
        request = {
            "plugin": "kamino",
            "function": "borrowlend",
            "args": {
                "walletAddress": wallet_id,
                "operation": operation,
                "currency": currency,
                "amount": amount,
            }
        }

        tx = self._generate_tx(request)
        return await self._send_and_wait(tx)


class KaminoBalanceUtility(RemoteUtility):
    name = "kamino-balance"
    description = "A utility that allows you to get your Kamino balance"

    async def run(self, wallet_id: str) -> str:
        request = {
            "plugin": "kamino",
            "function": "balance",
            "walletAddress": wallet_id,
        }

        return self._get_remote_response(request)
