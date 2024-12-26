from typing import Literal

from fridonai_core.plugins.tools import BaseTool
from fridonai_core.plugins.tools.base import BaseToolInput
from pydantic import Field

from settings import settings

if settings.ENV == "mock":
    pass
else:
    from libs.community.plugins.coin_observer.utilities import CoinObserverUtility


class CoinObserverToolInput(BaseToolInput):
    coin_name: str = Field(..., description="The name of the coin to observe")
    interval: Literal["1h", "4h", "1d", "1w"] = Field(
        default="1h", description="The interval of the technical indicators"
    )
    filter: str = Field(
        ..., description="The filter text query to use for the technical indicators"
    )
    recurring: bool = Field(
        default=False, description="Whether the notification is recurring."
    )


CoinObserverTool = BaseTool(
    name="coin-observer",
    description="A utility that allows you to set notification for a coin with specific filters",
    args_schema=CoinObserverToolInput,
    utility=CoinObserverUtility(),
    examples=[
        {
            "request": "Notify me when the price of BTC is greater than 50000 and RSI is greater than 70",
            "response": "Notification set successfully",
        },
        {
            "request": "Notify me SOL volume is greater than 1000000 and MACD < 50",
            "response": "Notification set successfully",
        },
        {
            "request": "Set up a recurring notification for the price of BTC is greater than 50000 and RSI is greater than 70",
            "response": "Notification set successfully",
        },
    ],
)


TOOLS = [
    CoinObserverTool,
]
