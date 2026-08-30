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