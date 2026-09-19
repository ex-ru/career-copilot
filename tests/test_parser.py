"""
tests/test_parser.py - Unit tests for document parser.
"""

from pathlib import Path
import pytest
from core.parser import DocumentParser


def test_read_text_file(tmp_path: Path):
    sample_file = tmp_path / "test.txt"
    sample_file.write_text("Hello World! Привет мир!", encoding="utf-8")
    content = DocumentParser.read_text_file(sample_file)
    assert "Hello World!" in content
    assert "Привет мир!" in content


def test_scan_directory(tmp_path: Path):
    (tmp_path / "resume.md").write_text("# Resume", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("Notes text", encoding="utf-8")
    (tmp_path / "ignore.bin").write_bytes(b"\x00\x01\x02")

    scanned = DocumentParser.scan_directory(tmp_path)
    names = [doc["name"] for doc in scanned]
    assert "resume.md" in names
    assert "notes.txt" in names
    assert "ignore.bin" not in names
