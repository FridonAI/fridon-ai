from app.brain.chain import generate_response
from pydantic.v1 import BaseModel


class Chat:
    def __init__(self) -> None:
        pass

    async def process(self, chat_id: str, wallet_id: str, message: str) -> str | BaseModel:
        return await generate_response(chat_id, wallet_id, message)

