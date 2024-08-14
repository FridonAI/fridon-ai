from typing import Any

from app.core.plugins.utilities import BaseUtility


class BlockchainMockUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> str:
        return "Tx 12345 successfully completed!"

class RemoteMockUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> dict:
        return {"data": {"RSA": 23}}

class LLMMockUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> str:
        return "Fridon is Great"
