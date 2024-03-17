from app.adapters.blockchain import BlockchainAdapter
from app.brain.chain import generate_response


class Chat:
    def __init__(self) -> None:
        pass

    def process(self, message: str) -> str:
        return generate_response(message)

