from fastapi_camelcase import CamelModel


class UserInput(CamelModel):
    wallet_id: str


class DataInput(CamelModel):
    message: str


class Request(CamelModel):
    chat_id: str
    user: UserInput
    data: DataInput
    aux: dict


class ResponseDto(Request):
    def __str__(self):
        import json
        return json.dumps(self.dict())

