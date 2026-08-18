from pathlib import Path


PROJECT_ROOT = Path("workspace")


def list_files() -> list[str]:
    """Return all files in the workspace."""

    if not PROJECT_ROOT.exists():
        return []

    return [
        str(path.relative_to(PROJECT_ROOT))
        for path in PROJECT_ROOT.rglob("*")
        if path.is_file()
    ]


def read_file(path: str) -> str:
    """Read a file from the workspace."""

    file_path = PROJECT_ROOT / path

    if not file_path.exists():
        raise FileNotFoundError(path)

    return file_path.read_text()


def write_file(path: str, content: str) -> str:
    """Write a file to the workspace."""

    file_path = PROJECT_ROOT / path

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path.write_text(content)

    return f"Successfully wrote {path}"