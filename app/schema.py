from fastapi_camelcase import CamelModel


class UserInput(CamelModel):
    wallet_id: str


class DataInput(CamelModel):
    message: str | dict
    message_id: str | None = None
    plugins: list[str] = ["greeter", "wallet", "kamino", "jupyter", "symmetry", "coin-price-chart-similarity-search", "coin-technical-analyzer"]


class DataRequestInput(CamelModel):
    message: str | dict | None = None
    message_id: str | None = None
    plugins_used: list[str] | None = None
    serialized_transaction: list[int] | None = None
    id: str | None = None


class Request(CamelModel):
    chat_id: str
    user: UserInput
    data: DataInput
    aux: dict


class ResponseDto(CamelModel):
    chat_id: str
    user: UserInput
    data: DataRequestInput
    aux: dict

    def __str__(self):
        import json
        return json.dumps({"data": self.dict()})

    @staticmethod
    def from_params(chat_id: str, wallet_id: str, message: str | dict | None, serialized_transaction: dict | None, id: str, aux: dict):
        return ResponseDto(chat_id=chat_id, user=UserInput(wallet_id=wallet_id), data=DataRequestInput(message=message, serialized_transaction=serialized_transaction, id=id), aux=aux)



