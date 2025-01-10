import os 
from langchain_openai import ChatOpenAI

chat_gpt_model = ChatOpenAI(
    model="gpt-4o", 
    temperature=0, 
    api_key=os.environ.get("OPENAI_API_KEY"), 
    verbose=True
)

chat_gpt_model_mini = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY"),
    verbose=True,
)


def get_model(name="gpt-4o"):
    if name == "gpt-4o":
        return chat_gpt_model
    elif name == "gpt-4o-mini":
        return chat_gpt_model_mini
    else:
        return chat_gpt_model


def create_structured_output_model(output_format, model=chat_gpt_model):
    return model.with_structured_output(output_format)

