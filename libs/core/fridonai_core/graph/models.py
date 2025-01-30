import os 
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_together import ChatTogether

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

deepseek_v3 = BaseChatOpenAI(
    model="deepseek-chat",
    openai_api_key="sk-7ed74465fc20437184a61bf5a20229b2",
    openai_api_base="https://api.deepseek.com",
    max_tokens=1024,
)

deepseek_v3_together = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0,
    together_api_key="6525e1be995840f2a2e13d4d31a476c7aaf7e40d11a0a329693bf677450b8db0",
)


def get_model(name="gpt-4o"):
    if name == "gpt-4o":
        return chat_gpt_model
    elif name == "gpt-4o-mini":
        return chat_gpt_model_mini
    else:
        return deepseek_v3_together


def create_structured_output_model(output_format, model=chat_gpt_model):
    return model.with_structured_output(output_format)

