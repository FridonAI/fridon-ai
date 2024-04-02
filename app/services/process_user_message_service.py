from app.brain.chat import Chat
import asyncio


class ProcessUserMessageService:
    def __init__(self) -> None:
        pass

    async def process(self, wallet_id: str, chat_id: str, personality: str, message: str) -> str:
        print(f"(Service) Processing Message: {message}, from User: {wallet_id}, with Personality: {personality} in Session: {chat_id}")
        chat = Chat(chat_id, wallet_id, personality)
        response = await chat.process(message)
        return response
