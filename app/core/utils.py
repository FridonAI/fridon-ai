import functools

from app.core.utilities import BlockchainUtility, RemoteUtility


def blockchain(func):
    @functools.wraps(func)
    async def wrapper(self: BlockchainUtility, *args, **kwargs):
        request = await func(self, *args, **kwargs)
        config = kwargs.get('config')

        if not config:
            raise ValueError("Missing 'config' in kwargs")

        wallet_id = config.get("wallet_id", "")
        chat_id = config.get("chat_id", "")
        request["args"]["walletAddress"] = wallet_id

        tx = self._generate_tx(request)
        result = await self._send_and_wait(tx, wallet_id, chat_id)

        return result

    return wrapper


def remote(func):
    @functools.wraps(func)
    async def wrapper(self: RemoteUtility, *args, **kwargs):
        request = await func(self, *args, **kwargs)
        config = kwargs.get('config')

        if not config:
            raise ValueError("Missing 'config' in kwargs")

        wallet_id = config.get("wallet_id", "")
        request["args"]["walletAddress"] = wallet_id

        return self._get_remote_response(request)
