from dependency_injector.wiring import inject, Provide

from app.brain.chat import Chat
import asyncio


class ProcessUserMessageService:
    @inject
    def __init__(
            self,
            literal_client=Provide["literal_client"]
    ) -> None:
        self.literal_client = literal_client

    def _send_literal_message(self, thread_id, thread_name, message_type, message_name, message):
        try:
            with self.literal_client.thread(thread_id=thread_id, name=thread_name) as thread:
                self.literal_client.message(content=message, type=message_type, name=message_name)
        except Exception as e:
            print(f"Error sending message to literal: {e}")

    async def process(self, wallet_id: str, chat_id: str, personality: str, message: str) -> str:
        print(f"(Service) Processing Message: {message}, from User: {wallet_id}, with Personality: {personality} in Session: {chat_id}")
        chat = Chat(chat_id, wallet_id, personality)
        self._send_literal_message(chat_id, wallet_id, "user_message", f"User", message)
        response = await chat.process(message)
        self._send_literal_message(chat_id, wallet_id, "assistant_message", f"Fridon", response)
        return response
