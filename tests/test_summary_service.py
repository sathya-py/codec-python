from __future__ import annotations

from pathlib import Path
import logging

from codex.services import SummaryService


def test_Given_files_When_creating_summary_Then_writes_output(tmp_path: Path):
    base = tmp_path / "src"
    base.mkdir()
    f1 = base / "a.py"
    f1.write_text("print('hello')\n")

    output = tmp_path / "summary.txt"
    service = SummaryService(logging.getLogger("test"))
    res = service.create_summary([f1], output, base, include_full_path=False)

    assert res.is_success
    text = output.read_text(encoding="utf-8")
    assert "Path: a.py" in text
    assert "print('hello')" in text
