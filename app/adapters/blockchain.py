from typing import Any


class BlockchainAdapter:
    def get_result(self, params: str | dict[str, Any]) -> str:
        return "Transaction successfully completed."
