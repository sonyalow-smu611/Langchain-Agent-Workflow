"""
Shared LLM factory used by every vibecoder agent.

Run: not run directly — imported as
     `from vibecoder.src.agents.base import get_llm`.

Learn: centralizing model config (name via MODEL_NAME env var, temperature)
in one place so every agent stays consistent, and loading the shared
repo-root .env from deep inside a package via
Path(__file__).resolve().parents[N].
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def get_llm():

    return ChatOpenAI(
        model=os.getenv(
            "MODEL_NAME",
            "gpt-4.1-mini"
        ),
        temperature=0
    )
