from __future__ import annotations

from dataclasses import dataclass
import webbrowser
from pathlib import Path
from typing import Sequence

from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Checkbox, Input, Static, Header, Footer

from codex.controller import CodecController
from codex.dtos import DiscoveryInput, SummaryInput
from codex.failure import Failure


class CodecTuiApp(App):

    # Visible shortcuts in the Footer
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("r", "run", "Run"),
        ("g", "open_github", "GitHub"),
    ]

    def __init__(
        self,
        controller: CodecController,
        default_extensions: Sequence[str],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.controller = controller
        self._default_extensions = tuple(default_extensions)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(Panel("Codec - An Application for Consolidation", title="CodeCollator 4", expand=False))
        yield Vertical(
            Input(placeholder="Directory", id="directory_input"),
            Input(placeholder="Output file", value="summary.txt", id="output_input"),
            Input(
                placeholder="Valid extensions (comma or space separated)",
                value=" ".join(self._default_extensions),
                id="extensions_input",
            ),
            Input(placeholder="Skip extensions", id="skip_input"),
            Input(placeholder="Skip folders", id="skip_folders_input"),
            Checkbox(label="Include full path", id="full_path_checkbox"),
            Button(label="Start", id="start_button"),
            Static("Status will appear here", id="status_output"),
        )
        yield Static(Panel("[link=https://github.com/sathya-py/codec-python]GitHub: sathya-py/codec-python[/link] | © 2025 CodeColater v4.0", expand=False))
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "start_button":
            return

        self.call_later(self._handle_submit)

    def _handle_submit(self) -> None:
        inputs = self._gather_inputs()
        discovery_result = self.controller.discover(inputs.discovery)
        if discovery_result.is_failure:
            self._update_status(discovery_result.error)
            return

        files = discovery_result.value or []
        summary_input = SummaryInput(
            files=files,
            output_path=inputs.output,
            base_directory=inputs.discovery.directory,
            include_full_path=inputs.include_full_path,
        )
        summary_result = self.controller.summarize(summary_input)
        if summary_result.is_failure:
            self._update_status(summary_result.error)
            return

        self._update_status(Failure('success', f"Summary written to {summary_input.output_path}"))

    # Key-bound actions
    def action_quit(self) -> None:  # q / ctrl+c
        self.exit()

    def action_run(self) -> None:  # r
        self._handle_submit()

    def action_open_github(self) -> None:  # g
        webbrowser.open_new_tab("https://github.com/sathya-py/codec-python")

    def _gather_inputs(self) -> 'TuiInputs':
        directory_value = self.query_one("#directory_input", Input).value.strip()
        output_value = self.query_one("#output_input", Input).value.strip() or "summary.txt"
        extensions_raw = self.query_one("#extensions_input", Input).value
        skip_raw = self.query_one("#skip_input", Input).value
        skip_folders_raw = self.query_one("#skip_folders_input", Input).value
        include_full = self.query_one("#full_path_checkbox", Checkbox).value

        return TuiInputs(
            discovery=DiscoveryInput(
                directory=Path(directory_value),
                valid_extensions=self._parse_extensions(extensions_raw, self._default_extensions),
                skip_extensions=self._parse_extensions(skip_raw, ()),
                skip_folders=self._parse_extensions(skip_folders_raw, ()),
            ),
            output=Path(output_value),
            include_full_path=include_full,
        )

    def _parse_extensions(self, raw: str, fallback: Sequence[str]) -> Sequence[str]:
        tokens = [token.strip() for token in raw.replace(',', ' ').split() if token.strip()]
        if not tokens:
            return tuple(fallback)
        return tuple(token if token.startswith('.') else f".{token}" for token in tokens)

    def _update_status(self, failure: Failure) -> None:
        status_text = failure.message
        status_widget = self.query_one("#status_output", Static)
        status_widget.update(Panel(status_text, title=failure.code))


@dataclass(frozen=True)
class TuiInputs:
    discovery: DiscoveryInput
    output: Path
    include_full_path: bool
