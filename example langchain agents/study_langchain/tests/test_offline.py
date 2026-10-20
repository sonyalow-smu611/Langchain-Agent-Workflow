"""
Offline tests: the whole CLI runs through run_chat() with a fake chat model
and fake embeddings, so no API key or network is needed.

Run: `pytest -m "not live"` from study_langchain/.
"""

import subprocess
import sys
import warnings
from pathlib import Path

import pytest

import study_resource_generator as app

NOTES = """Mitochondria

The mitochondrion is the site of aerobic respiration in the cell.
It produces ATP through oxidative phosphorylation.
"""


@pytest.fixture
def notes(documents):
    (documents / "biology.txt").write_text(NOTES)
    return documents


@pytest.mark.parametrize(
    "choice, heading",
    [
        ("1", "--- Cheatsheet ---"),
        ("cheatsheet", "--- Cheatsheet ---"),
        ("2", "--- Summary ---"),
        ("summary", "--- Summary ---"),
        ("3", "--- Notes ---"),
        ("In depth organised notes", "--- Notes ---"),
        ("4", "--- Quiz ---"),
        ("QUIZ", "--- Quiz ---"),
    ],
)
def test_each_menu_choice_prints_its_resource(run_cli, fake_models, notes, choice, heading):

    output = run_cli(choice, "mitochondria", "exit")

    assert f"{heading}\nFAKE REPLY 1" in output
    assert "Source: biology.txt" in fake_models[0]
    assert "Focus:\nmitochondria" in fake_models[0]


def test_invalid_choice_shows_the_menu_again(run_cli, fake_models, notes):

    output = run_cli("9", "exit")

    assert "Please choose 1, 2, 3, 4, or exit." in output
    assert output.count("Choose a study resource to generate:") == 2
    assert fake_models == []


def test_empty_topic_is_rejected_without_a_model_call(run_cli, fake_models, notes):

    output = run_cli("1", "   ", "exit")

    assert "Please enter a topic, chapter, or question." in output
    assert fake_models == []


def test_empty_documents_folder_explains_what_to_add(run_cli, fake_models, documents):

    output = run_cli("exit")

    assert f"No .txt study resources found in {documents}." in output
    assert "Choose a study resource" not in output
    assert fake_models == []


def test_second_request_sees_the_first_in_chat_history(run_cli, fake_models, notes):

    run_cli("1", "mitochondria", "4", "ATP", "exit")

    assert len(fake_models) == 2
    assert "Human: Generate cheatsheet for: mitochondria" in fake_models[1]
    assert "AI: FAKE REPLY 1" in fake_models[1]


def test_missing_api_key_says_where_to_put_it(run_cli, fake_models, notes, monkeypatch):

    monkeypatch.delenv("OPENAI_API_KEY")

    with pytest.raises(SystemExit) as exit_info:
        run_cli("1", "mitochondria", "exit")

    assert exit_info.value.code != 0
    assert str(exit_info.value) == (
        "OPENAI_API_KEY is not set. Add it to "
        f"{app.ENV_PATH} (copy .env.example to get started)."
    )
    assert fake_models == []


@pytest.mark.parametrize(
    "answers",
    [(), ("1",)],
    ids=["at the menu", "at the topic prompt"],
)
def test_closed_input_exits_cleanly(run_cli, fake_models, notes, answers):

    output = run_cli(*answers)

    assert "---- Message History ----" in output
    assert fake_models == []


def test_import_raises_no_deprecation_warnings():

    result = subprocess.run(
        [sys.executable, "-W", "error::DeprecationWarning", "-c", "import study_resource_generator"],
        capture_output=True,
        text=True,
        cwd=Path(app.__file__).parent,
    )

    assert result.returncode == 0, result.stderr[-800:]


def test_a_run_raises_no_deprecation_warnings(run_cli, fake_models, notes):

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        run_cli("1", "mitochondria", "exit")

    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert deprecations == [], [str(w.message)[:200] for w in deprecations]


def test_notes_with_non_ascii_characters_load(run_cli, fake_models, documents):

    (documents / "french.txt").write_text(
        "Révolution française\n\nLa prise de la Bastille — 14 juillet 1789 « liberté ».",
        encoding="utf-8",
    )

    output = run_cli("1", "Bastille", "exit")

    assert "--- Cheatsheet ---" in output
    assert "« liberté »" in fake_models[0]


def test_a_rebuild_does_not_keep_notes_from_an_earlier_run(run_cli, fake_models, documents):

    (documents / "first.txt").write_text("Notes from the first run.")
    run_cli("1", "notes", "exit")

    (documents / "first.txt").unlink()
    (documents / "second.txt").write_text("Notes from the second run.")
    run_cli("1", "notes", "exit")

    assert "Source: first.txt" in fake_models[0]
    assert "Source: second.txt" in fake_models[1]
    assert "Source: first.txt" not in fake_models[1]
