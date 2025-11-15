from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Sequence

from codex.failure import Failure
from codex.file_reader import read_file_content
from codex.repositories import FileFinderRepository
from codex.result import Result


class DiscoveryService:
    def __init__(self, repository: FileFinderRepository):
        self._repository = repository

    def discover(
        self,
        directory: Path,
        valid_extensions: Sequence[str],
        skip_extensions: Sequence[str],
        skip_folders: Sequence[str],
    ) -> Result[list[Path], Failure]:
        return self._repository.find(directory, valid_extensions, skip_extensions, skip_folders)


class SummaryService:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def create_summary(
        self,
        files: Iterable[Path],
        output_path: Path,
        base_directory: Path,
        include_full_path: bool,
    ) -> Result[None, Failure]:
        try:
            with output_path.open('w', encoding='utf-8') as handle:
                for path in files:
                    line = str(path) if include_full_path else str(path.relative_to(base_directory))
                    handle.write(f"Path: {line}\n")
                    handle.write(f"{'=' * len(line)}\n")
                    handle.write(read_file_content(path))
                    handle.write('\n' + '-' * 49 + '\n')

            return Result.success(None)
        except OSError as error:
            self._logger.error("Unable to write summary", exc_info=error)
            return Result.failure(Failure('write_error', f"Could not write '{output_path}': {error}"))
