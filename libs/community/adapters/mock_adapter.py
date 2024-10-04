from fridonai_core.plugins.utilities.adapter_base import BaseAdapter


class MockAdapter(BaseAdapter):
    async def send(self, *args, **kwargs) -> dict | str:
        pass
