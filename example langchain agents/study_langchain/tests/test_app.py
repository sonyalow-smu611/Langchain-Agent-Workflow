"""
Tests for the Streamlit front end (app.py), driven with Streamlit's AppTest:
the script runs in-process, so the same fake models and documents fixtures
used for the CLI apply here too.

Run: `pytest tests/test_app.py` from study_langchain/.
"""

from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture
def streamlit_app():
    # The retriever is cached across runs; start every test from a clean build.
    st.cache_resource.clear()
    at = AppTest.from_file(APP_PATH, default_timeout=120)
    at.run()
    return at


def markdown_text(at) -> str:
    return "\n".join(block.value for block in at.markdown)


@pytest.fixture
def notes(documents):
    (documents / "biology.txt").write_text(
        "The mitochondrion is the site of aerobic respiration. It produces ATP."
    )
    return documents


def ask(at, resource, topic):
    at.sidebar.radio[0].set_value(resource)
    at.chat_input[0].set_value(topic).run()
    assert not at.exception, at.exception


def test_generates_the_chosen_resource(fake_models, notes, streamlit_app):

    ask(streamlit_app, "Quiz", "mitochondria")

    assert "FAKE REPLY 1" in markdown_text(streamlit_app)
    assert "**Quiz:** mitochondria" in markdown_text(streamlit_app)
    assert "Source: biology.txt" in fake_models[0]
    assert "Human: Generate quiz for: mitochondria" in fake_models[0]


def test_second_request_sees_the_first_in_chat_history(fake_models, notes, streamlit_app):

    ask(streamlit_app, "Cheatsheet", "mitochondria")
    ask(streamlit_app, "Quiz", "ATP")

    assert len(fake_models) == 2
    assert "Human: Generate cheatsheet for: mitochondria" in fake_models[1]
    assert "AI: FAKE REPLY 1" in fake_models[1]
    assert "Human: Generate quiz for: ATP" in fake_models[1]


def test_empty_documents_folder_explains_what_to_add(fake_models, documents, streamlit_app):

    assert f"No .txt study resources found in `{documents}`" in streamlit_app.warning[0].value
    assert len(streamlit_app.chat_input) == 0


def test_missing_api_key_says_where_to_put_it(fake_models, notes, monkeypatch):

    monkeypatch.delenv("OPENAI_API_KEY")
    st.cache_resource.clear()
    at = AppTest.from_file(APP_PATH).run()

    assert "OPENAI_API_KEY is not set" in at.error[0].value
    assert len(at.chat_input) == 0
    assert fake_models == []


@pytest.mark.live
def test_live_cheatsheet_from_the_sample_notes(record_live_prompts, streamlit_app):

    ask(streamlit_app, "Cheatsheet", "Calvin cycle")

    answer = streamlit_app.chat_message[-1]
    assert answer.name == "assistant"
    assert "Source: photosynthesis.txt" in record_live_prompts[0]
    assert len(answer.markdown[0].value) > 200


@pytest.mark.live
def test_live_unrelated_topic_says_no_notes_matched(record_live_prompts, streamlit_app):

    ask(streamlit_app, "Cheatsheet", "French Revolution")

    assert "matched 'French Revolution'" in streamlit_app.warning[0].value
    assert record_live_prompts == []

    # The unmatched turn is not sent to the model as chat history.
    ask(streamlit_app, "Quiz", "Calvin cycle")

    assert len(record_live_prompts) == 1
    assert "French Revolution" not in record_live_prompts[0]
