from dependency_injector.wiring import Provide, inject

from app.schema import ResponseDto
from app.utils.redis import Publisher

from app.ram import chat_queues

import requests
import os


async def get_balance(**kwargs) -> str:
    return "Transaction successfully completed."


@inject
async def get_stake_borrow_lend_tx(
        provider: str,
        operation: str,
        currency: str,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
        **kwargs
) -> str:
    return "Stake successfully completed."


@inject
async def get_transfer_tx(
        to_wallet_id: str,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
) -> str:
    print("Sending request to blockchain")

    req = {
        "walletAddress": wallet_id,
        "toAddress": to_wallet_id,
        "mintAddress": "DFL1zNkaGPWm1BqAVqRjCZvHmwTFrEaJtbzJWgseoNJh",
        "amount": 10
    }
    apiUrl = os.environ["API_URL"]
    if not apiUrl:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(f"{apiUrl}/blockchain/transfer-tokens", json=req).json()

    await pub.publish("response_received", str(ResponseDto.from_params(chat_id, wallet_id, resp, {})))

    print("Waiting for response")
    response = await chat_queues[chat_id].get()
    print("Got Response", response)
    return "Transaction successfully completed."
