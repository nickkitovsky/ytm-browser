from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Label, Switch

from ytm_browser import start_endpoints
from ytm_browser.core import api_client
from ytm_browser.core.responses import AbstractResponse, parse_response


class LazyLoadCollapsible(Collapsible):
    """Changebe behavior for default 'Collapsible' for lazy loading child containers."""

    def __init__(
        self,
        *children: Widget,
        raw_response,
        title: str = "Toggle",
        collapsed: bool = True,
        collapsed_symbol: str = "▶",
        expanded_symbol: str = "▼",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        # START CREDENTIALS
        api_client.SyncClient.create_with_credentials(
            "files/auth/cmd.txt",
        )
        # END CREDENTIALS

        self.parsed_response = parse_response(raw_response)
        self._anchor = Label("")
        super().__init__(
            self._anchor,
            title=self.parsed_response.title,
            collapsed=collapsed,
            collapsed_symbol=collapsed_symbol,
            expanded_symbol=expanded_symbol,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def on_mount(self) -> None:
        self._is_mounted_response = False

    def _get_child_id(self, child: AbstractResponse) -> str:
        match child.payload:
            case {"playlistId": item_id} | {"videoId": item_id}:
                return f"_{item_id}"
            case _:
                msg = f"Not found id in:\n{child.payload}"
                raise AttributeError(msg)

    def _get_child_container(self) -> VerticalScroll:
        container = []
        for child in self.parsed_response.children:
            container.append(
                Grid(
                    Switch(animate=True),
                    Label(child.title),
                    # PlaylistCollapssible(playlist),
                    id=self._get_child_id(child=child),
                    classes="child_grid",
                ),
            )
        return VerticalScroll(*container)

    def _watch_collapsed(self, collapsed: bool) -> None:
        if not self.collapsed and not self._is_mounted_response:
            self.mount(self._get_child_container(), after=self._anchor)
        self._is_mounted_response = True
        return super()._watch_collapsed(collapsed)


class DevApp(App):
    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        yield LazyLoadCollapsible(raw_response=start_endpoints.library)


if __name__ == "__main__":
    app = DevApp()
    app.run()
