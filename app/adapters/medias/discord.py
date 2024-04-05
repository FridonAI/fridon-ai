import requests
import json
import os

from app.adapters.medias.schema import Media


async def _send_action(
        action: str,
        request: dict,
):
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.post(f"{api_url}/medias/{action}", json=request)

    if 500 > resp.status_code >= 400:
        return "Something went wrong!"
    if resp.status_code >= 500:
        return "Something went wrong! Please try again later."
    return f"Media successfully {action}ed!"


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


async def get_available_servers() -> str:
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.get(f"{api_url}/medias/").json()
    print("Available Medias Response", resp)
    if "statusCode" in resp:
        if 500 > resp["statusCode"] >= 400:
            return resp.get("message", "Something went wrong!")
        if resp["statusCode"] >= 500:
            return "Something went wrong! Please try again later."

    return 'Currently available medias: ' + ', '.join(server for server in resp['medias'])


async def get_wallet_servers(wallet_id) -> str:
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.get(f"{api_url}/medias/wallet/{wallet_id}").json()
    print("Wallet followed medias Response", resp)
    if "statusCode" in resp:
        if 500 > resp["statusCode"] >= 400:
            return resp.get("message", "Something went wrong!")
        if resp["statusCode"] >= 500:
            return "Something went wrong! Please try again later."
    if len(resp['medias']) == 0:
        return "You are not following any media."
    return 'Your followed media(s): ' + ', '.join(server for server in resp['medias'])


async def get_media_text(
        wallet_id: str,
        servers: list[str],
        date: str,
) -> str:
    def all_servers():
        return len(servers) == 1 and servers[0] == "all"

    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.get(f"{api_url}/medias/wallet/{wallet_id}").json()
    print("Wallet followed medias Response", resp)
    if "statusCode" in resp:
        if 500 > resp["statusCode"] >= 400:
            return resp.get("message", "Something went wrong!")
        if resp["statusCode"] >= 500:
            return "Something went wrong! Please try again later."

    wallet_medias = resp['medias']

    if all_servers():
        servers = wallet_medias
    else:
        servers = [server for server in servers if server in wallet_medias]

    whole_text = ""
    with open('./data/media.json', 'r') as f:
        data = json.load(f)
        for media, obj in data.items():
            if not all_servers() and media not in servers:
                continue
            for content in obj['contents']:
                if date <= content['createdAt']:
                    whole_text += content['content']
    return whole_text




