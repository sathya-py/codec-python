from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from codex.controller import CodecController
from codex.repositories import LocalFileFinder
from codex.services import DiscoveryService, SummaryService


class ServiceContainer:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger('codex')
        self.logger.setLevel(logging.INFO)
        self.repository = LocalFileFinder()
        self.discovery_service = DiscoveryService(self.repository)
        self.summary_service = SummaryService(self.logger)
        self.controller = CodecController(
            self.discovery_service,
            self.summary_service,
            self.logger,
        )

    def override_repository(self, repository: LocalFileFinder) -> None:
        self.repository = repository
        self.discovery_service = DiscoveryService(repository)
        self.controller = CodecController(
            self.discovery_service,
            self.summary_service,
            self.logger,
        )
