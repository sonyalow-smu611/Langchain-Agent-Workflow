"""
Shared LLM factory used by every vibecoder agent.

Run: not run directly — imported as
     `from vibecoder.src.agents.base import get_llm`.

Learn: centralizing model config (name via MODEL_NAME env var, temperature)
in one place so every agent stays consistent, and loading the vibecoder
folder's .env from deep inside a package via
Path(__file__).resolve().parents[N].
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

VIBECODER_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = VIBECODER_ROOT / "src" / "prompts"

load_dotenv(VIBECODER_ROOT / ".env")


def load_prompt(name: str) -> str:
    """Read a system prompt by file name, whatever the current directory is."""

    return (PROMPT_DIR / name).read_text()


def get_llm():

    return ChatOpenAI(
        model=os.getenv(
            "MODEL_NAME",
            "gpt-4.1-mini"
        ),
        temperature=0
    )
