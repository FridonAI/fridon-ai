from dependency_injector.wiring import Provide, inject

from app.brain.schema import DefiBalanceParameters, DefiStakeBorrowLendParameters, DefiTransferParameters

from app.schema import ResponseDto
from app.utils.redis import Publisher

from app.ram import chat_queues

import requests


async def get_balance(params: DefiBalanceParameters, **kwargs) -> str:
    return "Transaction successfully completed."


@inject
async def get_stake_borrow_lend_tx(params: DefiStakeBorrowLendParameters, chat_id: str, wallet_id: str, pub: Publisher = Provide["publisher"], **kwargs) -> str:
    return "Transaction successfully completed."


@inject
async def get_transfer_tx(
        params: DefiTransferParameters,
        chat_id: str,
        wallet_id: str,
        pub: Publisher = Provide["publisher"],
) -> str:
    # write urllib http post request
    print("Sending request to blockchain")

    req = {
        "walletAddress": wallet_id,
        "toAddress": params.wallet,
        "mintAddress": "DFL1zNkaGPWm1BqAVqRjCZvHmwTFrEaJtbzJWgseoNJh",
        "amount": 10
    }
    resp = requests.post("http://localhost:3000/blockchain/transfer-tokens", json=req).json()

    await pub.publish("response_received", str(ResponseDto.from_params(chat_id, wallet_id, resp, {})))

    print("Waiting for response")
    response = await chat_queues[chat_id].get()
    print("Got Response", response)
    return "Transaction successfully completed."


adapters = {
    DefiBalanceParameters: get_balance,
    DefiStakeBorrowLendParameters: get_stake_borrow_lend_tx,
    DefiTransferParameters: get_transfer_tx
}
