import pytest
from app.loaders import extract_text


def test_reads_txt_file():
    assert extract_text("notes.txt", b"hello world") == "hello world"


def test_reads_markdown_file():
    assert extract_text("readme.md", b"# Title") == "# Title"


def test_rejects_unknown_file_type():
    with pytest.raises(ValueError):
        extract_text("virus.exe", b"data")