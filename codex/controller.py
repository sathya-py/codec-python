from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from codex.dtos import DiscoveryInput, SummaryInput
from codex.failure import Failure
from codex.result import Result
from codex.services import DiscoveryService, SummaryService


class CodecController:
    def __init__(
        self,
        discovery_service: DiscoveryService,
        summary_service: SummaryService,
        logger: logging.Logger,
    ):
        self._discovery_service = discovery_service
        self._summary_service = summary_service
        self._logger = logger

    def discover(self, options: DiscoveryInput) -> Result[list[Path], Failure]:
        self._logger.info("Starting discovery")
        return self._discovery_service.discover(
            options.directory,
            options.valid_extensions,
            options.skip_extensions,
            options.skip_folders,
        )

    def summarize(self, options: SummaryInput) -> Result[None, Failure]:
        self._logger.info("Creating summary file")
        return self._summary_service.create_summary(
            options.files,
            options.output_path,
            options.base_directory,
            options.include_full_path,
        )
