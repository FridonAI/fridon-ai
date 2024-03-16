from adapters.blockchain import BlockchainAdapter

class Chat:
    def __init__(self):
        pass

    def process(self, message: str):
        blockchain = BlockchainAdapter()
        return blockchain.get_result(message)