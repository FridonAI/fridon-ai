from pydantic.v1 import BaseModel, root_validator


class BaseUtility(BaseModel):
    name: str
    description: str

    @root_validator
    def validate_environment(cls, values: dict) -> dict:
        return values

    def run(self, *args, **kwargs) -> str: ...
