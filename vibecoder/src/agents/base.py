import os

from langchain_openai import ChatOpenAI


def get_llm():

    return ChatOpenAI(
        model=os.getenv(
            "MODEL_NAME",
            "gpt-4.1-mini"
        ),
        temperature=0
    )
