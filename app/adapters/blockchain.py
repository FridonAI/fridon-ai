import json
import uuid

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

    if "statusCode" in resp:
        if 500 > resp["statusCode"] >= 400:
            return resp.get("message", "Something went wrong!")
        if resp["statusCode"] >= 500:
            return "Something went wrong! Please try again later."

    queue_name = str(uuid.uuid4())

    await pub.publish("response_received", str(ResponseDto.from_params(chat_id, wallet_id, None, resp["data"]["serializedTx"], queue_name, {})))

    print("Waiting for response", queue_name)
    response = await queue_getter.get(queue_name=queue_name)
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


@inject
async def get_swap_tx(
        currency_from: str,
        currency_to: str,
        amount: float,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
        queue_getter=Provide["queue_getter"],
) -> str:
    print("Sending request to blockchain")

    req = {
        "walletAddress": wallet_id,
        "fromToken": currency_from,
        "toToken": currency_to,
        "amount": amount
    }

    api_url = os.environ["API_URL"]
    request_url = f"{api_url}/blockchain/swap"

    return await _send_and_wait(chat_id, wallet_id, request_url, req, pub, queue_getter)


async def get_symmetry_baskets(
) -> str:
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(f"{api_url}/blockchain/symmetry/baskets").json()
    if "statusCode" in resp:
        if 500 > resp["statusCode"] >= 400:
            return resp.get("message", "Something went wrong!")
        if resp["statusCode"] >= 500:
            return "Something went wrong! Please try again later."
    print("Got Response", resp)
    return json.dumps(resp)


async def get_balance(
        wallet_id: str,
        provider: str,
        operation: str,
        currency: str,
):

    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    if currency == 'points' and operation == 'all':
        req = {
            "walletAddress": wallet_id,
            "provider": provider if provider != "wallet" else "all",
        }
        resp = requests.post(f"{api_url}/blockchain/points", json=req).json()
    else:
        req = {
            "walletAddress": wallet_id,
            "provider": provider,
            "currency": currency,
            "operation": operation,
        }
        resp = requests.post(f"{api_url}/blockchain/balance-operation", json=req).json()
    if "statusCode" in resp:
        if 500 > resp["statusCode"] >= 400:
            return resp.get("message", "Something went wrong!")
        if resp["statusCode"] >= 500:
            return "Something went wrong! Please try again later."
    print("Got Response", resp)
    return json.dumps(resp['data'])
