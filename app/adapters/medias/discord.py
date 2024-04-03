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

    try:
        resp = requests.post(f"{api_url}/medias/{action}", json=request).json()
    except Exception as e:
        print(e)
        return f'Failed to {action} server'
    print("Response", resp)
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


async def get_available_servers() -> str:
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.get(f"{api_url}/medias/").json()
    print("Available Servers Response", resp)
    return 'bonk, madlads, symmetry'
    # if resp['status'] == 200:
    # return ', '.join(server for server in resp['medias'])
    # return resp['data']


async def get_wallet_servers(wallet_id) -> str:
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    # resp = requests.get(f"{api_url}/medias/wallet/{wallet_id}").json()
    # print(resp)
    return "gaimin, jupiter"
    # if resp['status'] == 200:
    # return ', '.join(server for server in resp['medias'])
    # return resp['data']


async def get_media_text(
        servers: list[str],
        date: str,
) -> str:
    def all_servers():
        return len(servers) == 1 and servers[0] == "all"

    whole_text = ""
    with open('./data/media.json', 'r') as f:
        data = json.load(f)
        for media, obj in data.items():
            if not all_servers() and media not in servers:
                continue
            server_obj = Media.parse_obj(obj)
            for content in server_obj.contents:
                if date <= content.created_at:
                    whole_text += str(content)
    return whole_text




