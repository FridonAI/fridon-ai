import os 
from langchain_openai import ChatOpenAI

chat_gpt_model = ChatOpenAI(
    model="gpt-4o", 
    temperature=0, 
    api_key=os.environ.get("OPENAI_API_KEY"), 
    verbose=True
)

def get_model(name="gpt"):
    return chat_gpt_model


def create_structured_output_model(output_format, model=chat_gpt_model):
    return model.with_structured_output(output_format)

