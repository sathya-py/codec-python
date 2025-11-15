import argparse
import logging
import sys
from pathlib import Path
from typing import Sequence

from codex.container import ServiceContainer
from codex.dtos import DiscoveryInput, SummaryInput
from codex.tui import CodecTuiApp

DEFAULT_EXTENSIONS: tuple[str, ...] = (
    '.txt',
    '.py',
    '.c',
    '.cpp',
    '.h',
    '.cs',
    '.js',
    '.ts',
    '.jsx',
    '.html',
    '.css',
    '.json',
    '.yaml',
    '.yml',
    '.md',
    '.rs',
    '.go',
    '.dart',
    '.php',
    '.rb',
    '.sh',
    '.sql',
    '.xml',
    '.csv',
)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _normalize_extensions(raw: Sequence[str] | None, fallback: Sequence[str]) -> tuple[str, ...]:
    if not raw:
        return tuple(fallback)

    normalized: list[str] = []
    for extension in raw:
        candidate = extension.strip()
        if not candidate:
            continue
        normalized.append(candidate if candidate.startswith('.') else f'.{candidate}')

    return tuple(normalized) if normalized else tuple(fallback)


def _run_summary(args: argparse.Namespace, container: ServiceContainer) -> int:
    valid_extensions = _normalize_extensions(args.extensions, DEFAULT_EXTENSIONS)
    skip_extensions = _normalize_extensions(args.skip, ())
    skip_folders = tuple(args.skip_folders or [])

    discovery_input = DiscoveryInput(
        directory=Path(args.directory),
        valid_extensions=valid_extensions,
        skip_extensions=skip_extensions,
        skip_folders=skip_folders,
    )
    discovery_result = container.controller.discover(discovery_input)

    if discovery_result.is_failure:
        container.logger.error(discovery_result.error.message)
        return 1

    summary_input = SummaryInput(
        files=discovery_result.value or [],
        output_path=Path(args.output),
        base_directory=Path(args.directory),
        include_full_path=args.full_path,
    )
    summary_result = container.controller.summarize(summary_input)
    if summary_result.is_failure:
        container.logger.error(summary_result.error.message)
        return 1

    container.logger.info(f"Summary created: {args.output}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description='Find code files, summarize content, and optionally run the TUI.')
    parser.add_argument('directory', nargs='?', help='Directory to search')
    parser.add_argument('-o', '--output', default='summary.txt', help='Summary file name')
    parser.add_argument('-s', '--skip', nargs='*', help='Extensions to skip (e.g., .jpg)')
    parser.add_argument('-e', '--extensions', nargs='*', help='Valid extensions to scan')
    parser.add_argument('--full-path', action='store_true', help='Write full paths into the summary')
    parser.add_argument('--skip-folders', nargs='*', help='Folder names to ignore')
    parser.add_argument('--tui', action='store_true', help='Launch interactive Textual UI')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    configure_logging()
    container = ServiceContainer()

    if args.tui:
        CodecTuiApp(container.controller, DEFAULT_EXTENSIONS).run()
        return

    if not args.directory:
        parser.error('Directory is required when not running TUI.')

    exit_code = _run_summary(args, container)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
