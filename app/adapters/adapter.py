from app.adapters.blockchain import adapters as blockchain_adapters


class AdapterResolver:
    def __init__(self, chat_id, wallet_id):
        self.chat_id = chat_id
        self.wallet_id = wallet_id
        self.adapters = {
            **blockchain_adapters
        }

    async def call(self, obj):
        return await self.adapters[obj.__class__](obj, chat_id=self.chat_id, wallet_id=self.wallet_id)
