from app.adapters.blockchain import BlockchainAdapter


class Chat:
    def __init__(self) -> None:
        pass

    def process(self, message: str) -> str:
        blockchain = BlockchainAdapter()
        return blockchain.get_result(message)
