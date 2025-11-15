from __future__ import annotations

from pathlib import Path

from codex.repositories import LocalFileFinder


def test_Given_missing_directory_When_discovering_files_Then_returns_failure(tmp_path: Path):
    repo = LocalFileFinder()
    missing = tmp_path / "does_not_exist"
    result = repo.find(missing, [".py"], [], [])

    assert result.is_failure
    assert result.error is not None
    assert result.error.code == "not_found"


def test_Given_files_When_filtered_by_extensions_Then_only_matching_returned(tmp_path: Path):
    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "c.jpg").write_text("not relevant")

    repo = LocalFileFinder()
    result = repo.find(tmp_path, [".py", ".txt"], [".txt"], [])

    assert result.is_success
    files = {p.name for p in (result.value or [])}
    assert files == {"a.py"}
