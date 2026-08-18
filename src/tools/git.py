import subprocess


def git_diff() -> str:
    result = subprocess.run(
        ["git", "diff"],
        capture_output=True,
        text=True
    )

    return result.stdout


def git_status() -> str:
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True
    )

    return result.stdout