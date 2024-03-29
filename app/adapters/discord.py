
from app.schema import ResponseDto
from app.ram import chat_queues

import requests
import os


async def _send_action(
        action: str,
        request: dict,
):
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(f"{api_url}/medias/{action}", json=request).json()
    print(resp)
    return resp


async def follow_server(
        server: str,
        wallet_id: str,
) -> str:
    print("Following server")

    return await _send_action("follow", {
        "server": server,
        "walletId": wallet_id,
    })


async def unfollow_server(
        server: str,
        wallet_id: str,
) -> str:
    print("Unfollowing server")

    return await _send_action("unfollow", {
        "server": server,
        "walletId": wallet_id,
    })
