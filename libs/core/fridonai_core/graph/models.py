import os 
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI
from langchain_together import ChatTogether
from langchain_anthropic import ChatAnthropic


models = {}


def init_models():
    global models

    try:
        gpt_4o_model = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.environ.get("OPENAI_API_KEY"),
            verbose=True,
        )
        models["gpt-4o"] = gpt_4o_model
    except Exception as e:
        print(f"Failed to initialize gpt-4o model: {e}")

    try:
        gpt_4o_mini_model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.environ.get("OPENAI_API_KEY"),
            verbose=True,
        )
        models["gpt-4o-mini"] = gpt_4o_mini_model
    except Exception as e:
        print(f"Failed to initialize gpt-4o-mini model: {e}")

    try:
        claude_model = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0,
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            verbose=True,
        )
        models["claude-3-5-sonnet"] = claude_model
    except Exception as e:
        print(f"Failed to initialize claude-3-5-sonnet model: {e}")

    try:
        deepseek_v3 = BaseChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.environ.get("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com",
            max_tokens=1024,
        )
        models["deepseek"] = deepseek_v3
    except Exception as e:
        print(f"Failed to initialize deepseek model: {e}")

    try:
        deepseek_v3_together = ChatTogether(
            model="deepseek-ai/DeepSeek-V3",
            temperature=0,
            api_key=os.environ.get("TOGETHER_API_KEY"),
        )
        models["deepseek_together"] = deepseek_v3_together
    except Exception as e:
        print(f"Failed to initialize deepseek_together model: {e}")


def get_model(name="gpt-4o"):
    if name in models:
        return models[name]
    else:
        return models["gpt-4o"]


def create_structured_output_model(output_format, model_name="gpt-4o"):
    model = get_model(model_name)
    return model.with_structured_output(output_format)

