from typing import Type

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid, VerticalScroll
from textual.driver import Driver
from textual.widget import Widget
from textual.widgets import Collapsible, Label, Switch

from ytm_browser import start_endpoints
from ytm_browser.core import api_client, responses


class EndpointCollapsible(Collapsible):
    """Changebe behavior for default 'Collapsible' for lazy loading child containers."""

    def __init__(
        self,
        *children: Widget,
        response: responses.AbstractResponse,
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
            "files/auth/bash.txt",
        )
        # END CREDENTIALS
        self.response = response
        self._anchor = Label("")
        super().__init__(
            self._anchor,
            title=self.response.title,
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

    def _get_child_id(self, child: responses.AbstractResponse) -> str:
        match child.payload:
            case {"playlistId": item_id} | {"videoId": item_id}:
                return f"_{item_id}"
            case _:
                msg = f"Not found id in:\n{child.payload}"
                raise AttributeError(msg)

    def _get_child_container(self) -> VerticalScroll:
        response_childer: list[Grid | Label] = []
        for child in self.response.children:
            match child:
                case responses.AbstractResponse():
                    response_childer.append(
                        Grid(
                            Switch(animate=True),
                            EndpointCollapsible(response=child),
                            id=self._get_child_id(child=child),
                            classes="child_grid",
                        ),
                    )
                case responses.TrackResponse():
                    response_childer.append(
                        Label(
                            renderable=f"{child.artist} - {child.title} ({child.lenght})",
                            classes="height_auto",
                        ),
                    )
        return VerticalScroll(*response_childer)

    def _watch_collapsed(self, collapsed: bool) -> None:
        if not self.collapsed and not self._is_mounted_response:
            self.mount(self._get_child_container(), after=self._anchor)
        self._is_mounted_response = True
        return super()._watch_collapsed(collapsed)


class DevApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(
        self,
        start_responses: list[responses.AbstractResponse],
        driver_class: type[Driver] | None = None,
        css_path: str | None = None,
        watch_css: bool = False,
    ):
        self.start_responses = start_responses
        super().__init__(driver_class, css_path, watch_css)

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            *[
                EndpointCollapsible(response=response)
                for response in self.start_responses
            ],
        )


if __name__ == "__main__":
    app = DevApp(start_endpoints.endpoints)
    app.run()
