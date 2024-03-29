import requests
import os


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


async def get_available_servers() -> str:
    api_url = os.environ["API_URL"]
    if not api_url:
        raise Exception("API_URL not set in environment variables")

    resp = requests.get(f"{api_url}/medias/").json()
    print(resp)
    return 'bonk, madlads, symmetry'
    # if resp['status'] == 200:
    # return ', '.join(server for server in resp['medias'])
    # return resp['data']
