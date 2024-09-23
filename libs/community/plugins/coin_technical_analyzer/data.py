from contextvars import ContextVar

from pydantic import BaseModel, Field


class DataStore(BaseModel):
    token_summaries_list: list[dict] = Field(default_factory=list)
    token_tags_list: list[dict] = Field(default_factory=list)

    def read_token_summaries(self) -> list[dict]:
        return self.token_summaries_list

    def update_token_summaries(self, value: list[dict]):
        self.token_summaries_list = value

    def read_token_tags(self) -> list[dict]:
        return self.token_tags_list

    def update_token_tags(self, value: list[dict]):
        self.token_tags_list = value


var_data_store = ContextVar("data_store", default=DataStore())


def ensure_data_store() -> DataStore:
    return var_data_store.get()
