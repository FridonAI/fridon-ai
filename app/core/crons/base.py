from datetime import datetime

from aiocron import crontab
from pydantic.v1 import BaseModel


class BaseCron(BaseModel):
    name: str
    schedule: str

    def __call__(self) -> None:
        print(f"Running cron job {self.name} - {datetime.now()}")
        self._process()

    def start(self) -> None:
        self()
        crontab(self.schedule, self)

    def _process(self) -> None: ...

