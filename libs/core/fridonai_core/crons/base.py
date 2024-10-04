from datetime import datetime

from aiocron import crontab
from pydantic import BaseModel


class BaseCron(BaseModel):
    name: str
    schedule: str

    async def arun(self) -> None:
        print(f"Running cron job {self.name} - {datetime.now()}")
        await self._process()

    async def start(self) -> None:
        await self.arun()
        crontab(self.schedule, self.arun)

    async def _process(self) -> None: ...
