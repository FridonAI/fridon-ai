from app.brain.chat import Chat


class ProcessUserMessageService:
    def __init__(self) -> None:
        pass

    async def process(self, user_id: str, chat_id: str, message: str) -> str:
        print(f"(Service) Processing Message: {message}, from User: {user_id}, in Session: {chat_id}")
        chat = Chat()
        result = chat.process(message)
        return result
