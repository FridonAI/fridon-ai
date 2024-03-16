class ProcessUserMessageService:
    def __init__(self) -> None:
        pass

    async def process(self, user_id: str, session_id: str, message: str) -> str:
        return message
