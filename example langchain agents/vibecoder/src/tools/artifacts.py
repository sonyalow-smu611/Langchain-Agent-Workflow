"""
Save/load arbitrary JSON blobs to artifacts/<name>.json — a simple way for
agents to persist intermediate results to disk.

Run: not run directly — imported wherever an agent wants to checkpoint
     output (e.g. saving a BlueprintSpec so a later step can reload it).

Learn: the save/load-to-disk pattern as the simplest possible alternative to
a database or LangGraph checkpointer for persisting agent output.
"""

import json
from pathlib import Path


ARTIFACT_DIR = Path("artifacts")


def save_artifact(name: str, data: dict) -> str:

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path = ARTIFACT_DIR / f"{name}.json"

    path.write_text(
        json.dumps(
            data,
            indent=2
        )
    )

    return str(path)


def load_artifact(name: str) -> dict:

    path = ARTIFACT_DIR / f"{name}.json"

    return json.loads(
        path.read_text()
    )