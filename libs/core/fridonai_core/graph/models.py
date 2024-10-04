from langchain_openai import ChatOpenAI

from fridonai_core.graph.tools import FinalResponse
from settings import settings

chat_gpt_model = ChatOpenAI(
    model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY, verbose=True
)


def get_model(name="gpt"):
    return chat_gpt_model


def create_structured_output_model(output_format, model=chat_gpt_model):
    return model.with_structured_output(output_format)


structured_final_response_model = create_structured_output_model(FinalResponse)
