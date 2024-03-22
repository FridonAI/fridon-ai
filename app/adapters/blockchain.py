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
        amount: float,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
        **kwargs
) -> str:
    print(f"Sending {operation} request to blockchain!")

    req = {
        "walletAddress": wallet_id,
        "provider": provider,
        "currency": currency,
        "operation": operation,
        "amount": amount,
    }

    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(f"{api_url}/blockchain/defi-operation", json=req).json()

    await pub.publish("response_received", str(ResponseDto.from_params(chat_id, wallet_id, resp, None, {})))

    print("Waiting for response")
    response = await chat_queues[chat_id].get()
    print("Got Response", response)
    return "Transaction successfully completed."


@inject
async def get_transfer_tx(
        to_wallet_id: str,
        currency: str,
        amount: float,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
) -> str:
    print("Sending request to blockchain")

    req = {
        "walletAddress": wallet_id,
        "toAddress": to_wallet_id,
        "currency": currency,
        "amount": amount
    }
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(f"{api_url}/blockchain/transfer-tokens", json=req).json()

    await pub.publish("response_received", str(ResponseDto.from_params(chat_id, wallet_id, None, resp['data']['serializedTx'], {})))

    print("Waiting for response")
    response = await chat_queues[chat_id].get()
    print("Got Response", response)
    return response
