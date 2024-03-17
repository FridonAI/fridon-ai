from pydantic.v1 import BaseModel
import json
from app.brain.chat import Chat


class ProcessUserMessageService:
    def __init__(self) -> None:
        pass

    async def process(self, user_id: str, chat_id: str, message: str) -> str:
        print(f"(Service) Processing Message: {message}, from User: {user_id}, in Session: {chat_id}")
        chat = Chat()
        try:
            result = chat.process(message)
        except Exception as e:
            print("Something went wrong!", e)
            return "I'm sorry, something went wrong. Please try again with different wording."
        if isinstance(result, BaseModel):
            return json.dumps(result.dict())
        return result
