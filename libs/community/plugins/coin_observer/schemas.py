import uuid
from pydantic import BaseModel, Field


class CoinObserverRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="The id of the observer record.")
    coin: str = Field(..., description="The coin name.")
    interval: str = Field(..., description="The interval of the coin.")
    filters: str = Field(..., description="The filters for the coin.")
    recurring: bool = Field(
        default=False, description="Whether the notification is recurring."
    )
