import os 
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_together import ChatTogether
from langchain_anthropic import ChatAnthropic

gpt_4o_model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY"),
    verbose=True,
)

gpt_4o_mini_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY"),
    verbose=True,
)

claude_model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
    verbose=True,
)

deepseek_v3 = BaseChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.environ.get("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    max_tokens=1024,
)

deepseek_v3_together = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0,
    api_key=os.environ.get("TOGETHER_API_KEY"),
)


def get_model(name="gpt-4o"):
    if name == "gpt-4o":
        return gpt_4o_model
    elif name == "gpt-4o-mini":
        return gpt_4o_mini_model
    elif name == "claude-3-5-sonnet":
        return claude_model
    elif name == "deepseek":
        return deepseek_v3_together
    else:
        return gpt_4o_model


def create_structured_output_model(output_format, model=gpt_4o_model):
    return model.with_structured_output(output_format)

