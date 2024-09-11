"""Download tab custom widgets."""

from typing import TYPE_CHECKING

from textual import on, work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Button, Static

from ytm_browser.core import downloader

if TYPE_CHECKING:
    from ytm_browser.textual_ui.app import YtMusicApp


class QueueTable(Static):
    """Widget for download tab with 'start download' button and queue table."""

    class UpdateCellMessage(Message):
        """Custom message with cell update data."""

        def __init__(self, cell_key: str, cell_value: str) -> None:
            self.cell_key = cell_key
            self.cell_value = cell_value
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Button.success(
            label="Start download", id="start_download_button"
        )
        yield VerticalScroll(self.app.download_table)

    def on_mount(self) -> None:
        """Set up table settings."""
        self.app: YtMusicApp  # define type for self.app for better work IDE
        self.app.download_table.cursor_type = "row"
        self.app.download_table.zebra_stripes = True
        self.table_titles = ("playlist", "status")
        self.app.download_table.add_column(
            label=self.table_titles[0],
            key=self.table_titles[0],
        )
        self.app.download_table.add_column(
            label=self.table_titles[1],
            key=self.table_titles[1],
            default="wait",
        )

    @on(Button.Pressed, "#start_download_button")
    def _start_download_handler(self) -> None:
        self._start_download()

    @work(thread=True)
    def _start_download(self) -> None:
        for playlist_key, playlist_object in self.app.download_queue.items():
            self.post_message(
                QueueTable.UpdateCellMessage(
                    cell_key=playlist_key,
                    cell_value="download",
                ),
            )
            downloader.download_playlist(
                playlist=playlist_object,
                target_dir=self.app.app_paths["download_dir"],
            )
            self.post_message(
                QueueTable.UpdateCellMessage(
                    cell_key=playlist_key, cell_value="done"
                )
            )

    @on(message_type=UpdateCellMessage)
    def _update_cell(self, message: UpdateCellMessage) -> None:
        self.app.download_table.update_cell(
            row_key=message.cell_key,
            column_key=self.table_titles[1],
            value=message.cell_value,
            update_width=True,
        )
