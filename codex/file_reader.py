from __future__ import annotations

import gzip
from pathlib import Path

import chardet


def detect_encoding(file_path: Path) -> str:
    with open(file_path, 'rb') as handle:
        sample = handle.read(4096)
    result = chardet.detect(sample)
    return result['encoding'] or 'utf-8'


def read_file_content(file_path: Path) -> str:
    if file_path.suffix.lower() == '.gz':
        with gzip.open(file_path, 'rb') as handle:
            return handle.read().decode('utf-8', errors='replace')

    encoding = detect_encoding(file_path)
    with file_path.open('r', encoding=encoding, errors='replace') as handle:
        return handle.read()
