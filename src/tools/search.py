from pathlib import Path

from src.tools.filesystem import PROJECT_ROOT


def search_code(query: str) -> list[dict]:
    """Search for a string across project files."""

    results = []

    if not PROJECT_ROOT.exists():
        return results

    for path in PROJECT_ROOT.rglob("*"):

        if not path.is_file():
            continue

        try:
            content = path.read_text()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(
            content.splitlines(),
            start=1
        ):
            if query.lower() in line.lower():
                results.append({
                    "file": str(path.relative_to(PROJECT_ROOT)),
                    "line": line_number,
                    "content": line.strip()
                })

    return results