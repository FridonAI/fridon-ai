
from libs.core.plugins.utilities import BaseUtility


class BaseMockUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> str:
        pass

class BlockchainMockUtility(BaseMockUtility):
    async def arun(self, *args, **kwargs) -> str:
        return "Tx 12345 successfully completed!"

class RemoteMockUtility(BaseMockUtility):
    async def arun(self, *args, **kwargs) -> dict:
        return {"data": {"RSA": 23}}

class LLMMockUtility(BaseMockUtility):
    async def arun(self, *args, **kwargs) -> str:
        return "Fridon is Great"

