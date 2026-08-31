"""
Example pytest test for a filesystem tool — writes a file into the
sandboxed workspace, reads it back, and asserts round-trip content.

Run: `cd vibecoder && pytest` (or `pytest vibecoder/tests` from the repo
     root). Creates vibecoder/workspace/test.txt as a side effect.

Learn: testing a tool function against the real filesystem (not mocked) is
fine when the tool's whole job is file I/O — there's nothing meaningful
left to fake.
"""

from vibecoder.src.tools.filesystem import (
    write_file,
    read_file
)


def test_file_round_trip():

    write_file(
        "test.txt",
        "hello"
    )

    content = read_file(
        "test.txt"
    )

    assert content == "hello"
    