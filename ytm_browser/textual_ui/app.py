from typing import Literal

from textual import on
from textual.app import App, ComposeResult
from textual.driver import Driver
from textual.widgets import DataTable, Footer, Markdown, TabbedContent, TabPane

from ytm_browser.core import api_client, credentials, responses
from ytm_browser.textual_ui import browse_tab, download_tab, settings_tab


class YtMusicApp(App):
    """Youtube Music Textual Application."""

    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("s", "show_tab('settings')", "Settings"),
        ("b", "show_tab('browse')", "Browse"),
        ("d", "show_tab('download')", "Download list"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        start_responses: list[responses.AbstractResponse],
        driver_class: type[Driver] | None = None,
        css_path: str | None = None,
        watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self.start_responses = start_responses
        self.download_queue: dict[str, responses.PlaylistResponse] = {}
        self.download_table: DataTable = DataTable(id="download_table")
        self.app_paths: dict[
            Literal["download_dir", "credentials_dir"], str
        ] = {
            "download_dir": "files/music",
            "credentials_dir": "files/auth",
        }
        self.app_data: dict[Literal["auth_data"], list] = {
            "auth_data": [],
        }

    def compose(self) -> ComposeResult:
        """Compose app with tabbed content."""
        # Footer to show keys
        yield Footer()

        # Add the TabbedContent widget
        with TabbedContent(initial=settings_tab.ID):
            yield settings_tab.SettingsTabPane(
                settings_tab.TITLE,
                id=settings_tab.ID,
            )
            with TabPane("Browse", id="browse"):
                yield browse_tab.BrowseEndpointsWidget()
            with TabPane("Download list", id="download"):
                yield download_tab.QueueTable()

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab

    @on(TabbedContent.TabActivated, pane="#browse")
    def switch_to_home(self) -> None:
        api_client.SyncClient.create_with_credentials(
            credentials.parse_curl_request(
                self.app_data["auth_data"],
            ),
        )
