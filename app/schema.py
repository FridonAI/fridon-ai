from fastapi_camelcase import CamelModel


class UserInput(CamelModel):
    wallet_id: str


class DataInput(CamelModel):
    message: str | dict 

class DataRequestInput(CamelModel):
    message: str | dict | None
    serialized_transaction: list[int] | None

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
    def from_params(chat_id: str, wallet_id: str, message: str | dict | None, serialized_transaction: dict | None, aux: dict):
        return ResponseDto(chat_id=chat_id, user=UserInput(wallet_id=wallet_id), data=DataRequestInput(message=message, serialized_transaction=serialized_transaction), aux=aux)



