from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class DiscoveryInput:
    directory: Path
    valid_extensions: Sequence[str]
    skip_extensions: Sequence[str]
    skip_folders: Sequence[str]


@dataclass(frozen=True)
class SummaryInput:
    files: Sequence[Path]
    output_path: Path
    base_directory: Path
    include_full_path: bool
