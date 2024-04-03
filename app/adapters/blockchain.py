from dependency_injector.wiring import Provide, inject

from app.schema import ResponseDto
from app.utils.redis import Publisher

import requests
import os


async def _send_and_wait(chat_id, wallet_id, request_url, request, pub, queue_getter):
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(request_url, json=request).json()

    await pub.publish("response_received", str(ResponseDto.from_params(chat_id, wallet_id, None, resp['data']['serializedTx'], {})))

    print("Waiting for response", chat_id)
    response = await queue_getter.get(queue_name=chat_id)
    print("Got Response", response)
    return response



@inject
async def get_stake_borrow_lend_tx(
        provider: str,
        operation: str,
        currency: str,
        amount: float,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
        queue_getter=Provide["queue_getter"],
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
    request_url = f"{api_url}/blockchain/defi-operation"

    return await _send_and_wait(chat_id, wallet_id, request_url, req, pub, queue_getter)


@inject
async def get_transfer_tx(
        to_wallet_id: str,
        currency: str,
        amount: float,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
        queue_getter=Provide["queue_getter"],
) -> str:
    print("Sending request to blockchain")

    req = {
        "walletAddress": wallet_id,
        "toAddress": to_wallet_id,
        "currency": currency,
        "amount": amount
    }

    api_url = os.environ["API_URL"]
    request_url = f"{api_url}/blockchain/transfer-tokens"

    return await _send_and_wait(chat_id, wallet_id, request_url, req, pub, queue_getter)


async def get_balance(
        wallet_id: str,
        provider: str,
        operation: str,
        currency: str,
) -> str:
    req = {
        "walletAddress": wallet_id,
        "provider": provider,
        "currency": currency,
        "operation": operation,
    }
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(f"{api_url}/blockchain/balance-operation", json=req).json()
    print("Got Response", resp)
    return resp
