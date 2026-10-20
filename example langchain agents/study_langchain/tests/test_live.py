"""
Live tests: real OpenAI embeddings and chat model, using the bundled sample
document in documents/. Skipped when OPENAI_API_KEY is missing.

Run: `pytest -m live` from study_langchain/.
"""

import pytest

pytestmark = pytest.mark.live


# Short topics that appear in the sample. With Chroma's default L2 distance,
# "limiting factors" and "Melvin Calvin" scored below the 0.2 threshold.
@pytest.mark.parametrize(
    "topic",
    ["Calvin cycle", "limiting factors", "Melvin Calvin", "what is ATP used for?"],
)
def test_short_topic_retrieves_the_matching_notes(run_cli, record_live_prompts, topic):

    output = run_cli("1", topic, "exit")

    assert "--- Cheatsheet ---" in output
    assert len(record_live_prompts) == 1
    assert "Source: photosynthesis.txt" in record_live_prompts[0]


def test_unrelated_topic_says_no_notes_matched(run_cli, record_live_prompts):

    output = run_cli("1", "French Revolution", "exit")

    assert "No notes in" in output
    assert "matched 'French Revolution'" in output
    assert "--- Cheatsheet ---" not in output
    assert record_live_prompts == []
