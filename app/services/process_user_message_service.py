from app.brain.chat import Chat
from app.ram import chat_queues
import asyncio


class ProcessUserMessageService:
    def __init__(self) -> None:
        pass

    async def process(self, wallet_id: str, chat_id: str, personality: str, message: str) -> str:
        print(f"(Service) Processing Message: {message}, from User: {wallet_id}, with Personality: {personality} in Session: {chat_id}")
        if chat_id not in chat_queues:
            chat_queues[chat_id] = asyncio.Queue()
        chat = Chat(chat_id, wallet_id, personality)
        response = await chat.process(message)
        return response
