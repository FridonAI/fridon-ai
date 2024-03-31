from langchain_community.chat_message_histories.postgres import PostgresChatMessageHistory

from app.settings import settings


def get_chat_history(session_id):
    chat_history = PostgresChatMessageHistory(
        connection_string=settings.POSTGRES_DB_URL,
        session_id=session_id
    )
    return chat_history