**Code Collator (codex)**

A clean-architecture code collator with a CLI and TUI. It scans a directory for specified file extensions, optionally skips folders/extensions, and writes a consolidated summary with file paths and content.

**Key Features**

- Discovery + summary services separated via repository and controller layers.
- Result/Failure pattern for fail-fast error handling (no exceptions for control flow).
- TUI built with Textual + Rich; CLI fallback remains available.
- Dependency injection via a simple `ServiceContainer`.

**Install (uv)**

Project already initialized for uv. From the project root:

```powershell
uv sync
```

This will create `.venv` and install dependencies from `pyproject.toml`.

**Run**

- TUI (interactive):

```powershell
./dist/codec.exe --tui
```

- CLI (non-interactive):

```powershell
./dist/codec.exe <directory> -o summary.txt \
    -e .py .ts .json --skip-folders .git node_modules --full-path
```

**Options**

- `-o`, `--output`: Output summary file (default: `summary.txt`).
- `-s`, `--skip`: Extensions to skip (e.g., `.jpg .png`).
- `-e`, `--extensions`: Extensions to include (default preset).
- `--full-path`: Include absolute file paths rather than relative.
- `--skip-folders`: Folder names to ignore (e.g., `node_modules .git`).

**TUI Keys**

- `r`: Run discovery + summary
- `q` / `Ctrl+C`: Quit
- `g`: Open GitHub repo (https://github.com/sathya-py/codec-python)

**Architecture**

- Package: `codex/` with `repositories`, `services`, `controller`, `file_reader`, `result`, `failure`.
- Entry point: `codec3.py` for both CLI and TUI (`--tui`) while packaged as `codec.exe`.
- Tests to be added with Given_When_Then naming and AAA structure; goal ≥90% coverage.

**Contributing**

PRs welcome. Please follow SOLID/DRY/KISS/YAGNI, keep files <200 lines and functions <50 lines, and prefer composition over inheritance.
