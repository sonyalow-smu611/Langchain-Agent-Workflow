"""
Shared fixtures for the Study Resource Generator tests.

Run: `pytest -m "not live"` for the offline tests, `pytest -m live` for the
     tests that call OpenAI with the key in study_langchain/.env.

Learn: driving an interactive CLI from a test by scripting input(), and
swapping the chat model and embeddings for fakes at module level.
"""

import builtins
import os

import pytest
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.fake_chat_models import FakeListChatModel

import study_resource_generator as app


def pytest_collection_modifyitems(config, items):
    if os.environ.get("OPENAI_API_KEY"):
        return

    skip_live = pytest.mark.skip(reason="OPENAI_API_KEY is not set in study_langchain/.env")

    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


class Prompts(list):
    """Every prompt the chat model was sent, as plain text."""

    def joined(self) -> str:
        return "\n\n".join(self)


@pytest.fixture
def prompts():
    return Prompts()


@pytest.fixture
def record_live_prompts(monkeypatch, prompts):
    """Keep the real ChatOpenAI but record each prompt it is sent."""

    class RecordingChatOpenAI(app.ChatOpenAI):
        def invoke(self, input, *args, **kwargs):
            prompts.append(input.to_string())
            return super().invoke(input, *args, **kwargs)

    monkeypatch.setattr(app, "ChatOpenAI", RecordingChatOpenAI)
    return prompts


class SameVectorEmbeddings(Embeddings):
    """Every text gets the same vector, so every chunk always matches."""

    def embed_documents(self, texts):
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text):
        return [1.0, 0.0, 0.0]


@pytest.fixture
def fake_models(monkeypatch, prompts):
    """Offline: canned replies from the chat model, no embedding calls."""

    class RecordingFakeChat(FakeListChatModel):
        def invoke(self, input, *args, **kwargs):
            prompts.append(input.to_string())
            return super().invoke(input, *args, **kwargs)

    monkeypatch.setenv("OPENAI_API_KEY", "offline-test-key")

    replies = [f"FAKE REPLY {n}" for n in range(1, 11)]
    monkeypatch.setattr(app, "ChatOpenAI", lambda model: RecordingFakeChat(responses=replies))
    monkeypatch.setattr(app, "OpenAIEmbeddings", lambda model: SameVectorEmbeddings())
    return prompts


@pytest.fixture
def documents(monkeypatch, tmp_path):
    """Point the app at an empty temporary documents folder."""

    folder = tmp_path / "documents"
    folder.mkdir()
    monkeypatch.setattr(app, "documents_dir", str(folder))
    return folder


@pytest.fixture
def run_cli(monkeypatch, capsys):
    """Run run_chat() with scripted answers and return everything it printed.

    When the answers run out, input() raises EOFError, like a closed stdin.
    """

    def run(*answers):
        remaining = list(answers)

        def scripted_input(prompt=""):
            print(prompt, end="")
            if not remaining:
                raise EOFError
            answer = remaining.pop(0)
            print(answer)
            return answer

        monkeypatch.setattr(builtins, "input", scripted_input)
        app.run_chat()
        return capsys.readouterr().out

    return run
