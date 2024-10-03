from fastapi_camelcase import CamelModel


class UserInput(CamelModel):
    wallet_id: str


class DataInput(CamelModel):
    message: str | dict
    message_id: str | None = None


class ResultData(CamelModel):
    message: str | dict | None = None
    structured_messages: list[str] = []
    message_id: str | None = None
    plugins_used: list[str] | None = None
    serialized_transaction: list[int] | None = None
    id: str | None = None


class RequestMessage(CamelModel):
    chat_id: str
    user: UserInput
    data: DataInput
    plugins: list[str] = ["wallet", "fridon", "solana-bonk-educator"]
    aux: dict


class ResponseMessage(CamelModel):
    chat_id: str
    user: UserInput
    data: ResultData
    aux: dict

    def __str__(self):
        import json
        return json.dumps({"data": self.dict()})

    @staticmethod
    def from_params(chat_id: str, wallet_id: str, message: str | dict | None, serialized_transaction: dict | None, id: str, aux: dict):
        return ResponseMessage(chat_id=chat_id, user=UserInput(wallet_id=wallet_id), data=ResultData(message=message, serialized_transaction=serialized_transaction, id=id), aux=aux)



