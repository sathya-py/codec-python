from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Sequence

from codex.failure import Failure
from codex.result import Result


class FileFinderRepository(ABC):
    @abstractmethod
    def find(
        self,
        directory: Path,
        valid_extensions: Sequence[str],
        skip_extensions: Sequence[str],
        skip_folders: Sequence[str],
    ) -> Result[list[Path], Failure]:
        raise NotImplementedError()


class LocalFileFinder(FileFinderRepository):
    def find(
        self,
        directory: Path,
        valid_extensions: Sequence[str],
        skip_extensions: Sequence[str],
        skip_folders: Sequence[str],
    ) -> Result[list[Path], Failure]:
        if not directory.is_dir():
            return Result.failure(Failure('not_found', f"Directory '{directory}' does not exist"))

        file_paths: list[Path] = []

        try:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if d not in skip_folders]

                for name in files:
                    path = Path(root) / name
                    if self._should_include(path, valid_extensions, skip_extensions):
                        file_paths.append(path)

            return Result.success(file_paths)
        except OSError as error:
            return Result.failure(Failure('io_error', f"Failed to scan '{directory}': {error}"))

    def _should_include(
        self,
        path: Path,
        valid_extensions: Sequence[str],
        skip_extensions: Sequence[str],
    ) -> bool:
        suffix = path.suffix.lower()
        return suffix in valid_extensions and suffix not in skip_extensions
