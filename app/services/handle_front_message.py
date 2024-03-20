from app.ram import chat_queues


class HandleFrontMessageService:
    def __init__(self) -> None:
        pass

    async def handle(self, chat_id: str, data: dict):
        print("Adding message to queue")
        chat_queue = chat_queues[chat_id]
        chat_queue.put_nowait(data)

