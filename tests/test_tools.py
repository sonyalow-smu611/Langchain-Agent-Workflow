from src.tools.filesystem import (
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
    