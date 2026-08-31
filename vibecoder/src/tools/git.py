"""
Thin wrappers around `git diff` and `git status --short`, for agents that
need to inspect the current repo state.

Run: not run directly — imported wherever an agent/tool needs git context.

Learn: subprocess.run(capture_output=True, text=True) — the standard way to
shell out and capture a command's output as a string in Python.
"""

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