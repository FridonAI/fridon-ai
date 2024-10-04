
from typing import Optional
from pydantic import Field
from fridonai_core.plugins.utilities import BaseUtility
from fridonai_core.plugins.utilities.adapter_base import BaseAdapter

class BaseMockUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> str:
        pass
    model_config = {
        'ignored_types': (dict,)
    }

class BlockchainMockUtility(BaseMockUtility):
    communicator: Optional[BaseAdapter] = Field(default=None,exclude=True)

    async def arun(self, *args, **kwargs) -> str:
        return "Tx 12345 successfully completed!"

class RemoteMockUtility(BaseMockUtility):
    async def arun(self, *args, **kwargs) -> dict:
        return {"data": {"RSA": 23}}

class LLMMockUtility(BaseMockUtility):
    async def arun(self, *args, **kwargs) -> str:
        return "Fridon is Great"

