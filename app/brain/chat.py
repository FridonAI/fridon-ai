from app.adapters.blockchain import BlockchainAdapter
from app.brain.chain import generate_response
from pydantic.v1 import BaseModel


class Chat:
    def __init__(self) -> None:
        pass

    def process(self, message: str) -> str | BaseModel:
        return generate_response(message)

