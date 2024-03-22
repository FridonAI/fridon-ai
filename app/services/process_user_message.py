from pydantic.v1 import BaseModel
import json
from app.brain.chat import Chat
from app.ram import chat_queues
import asyncio


class ProcessUserMessageService:
    def __init__(self) -> None:
        pass

    async def process(self, wallet_id: str, chat_id: str, message: str) -> str:
        print(f"(Service) Processing Message: {message}, from User: {wallet_id}, in Session: {chat_id}")
        if chat_id not in chat_queues:
            chat_queues[chat_id] = asyncio.Queue()
        chat = Chat()
        try:
            result = await chat.process(chat_id, wallet_id, message)
        except Exception as e:
            print("Something went wrong!", e)
            return "I'm sorry, something went wrong. Please try again with different wording."
        if isinstance(result, BaseModel):
            return result.json()
        return result
