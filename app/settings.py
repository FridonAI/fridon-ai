from typing import Optional
from pydantic.v1 import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):

    OPENAI_API_KEY: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB_URL: str

    API_URL: str

    LANGCHAIN_TRACING_V2: Optional[str]
    LANGCHAIN_ENDPOINT: Optional[str]
    LANGCHAIN_API_KEY: Optional[str]
    LANGCHAIN_PROJECT: Optional[str]

    LITERAL_API_KEY: Optional[str]

    PINECONE_API_KEY: str

    BIRDEYE_API_KEY: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
