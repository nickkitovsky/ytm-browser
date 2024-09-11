from typing import TYPE_CHECKING

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, VerticalScroll
from textual.widget import Widget
from textual.widgets import Collapsible, Label, Static, Switch

from ytm_browser.core import responses

if TYPE_CHECKING:
    from textual.driver import Driver

    from ytm_browser.textual_ui.app import YtMusicApp


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
        self.app: YtMusicApp  # define type for self.app for better work IDE
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
        response_children: list[Grid | Label] = []
        for child in self.response.children:
            match child:
                case responses.AbstractResponse():
                    response_children.append(
                        Grid(
                            Switch(animate=True),
                            EndpointCollapsible(response=child),
                            id=self._get_child_id(child=child),
                            classes="child_grid",
                        ),
                    )
                case responses.TrackResponse():
                    response_children.append(
                        Label(
                            renderable=f"{child.artist} - {child.title} ({child.lenght})",
                            classes="height_auto",
                        ),
                    )
        return VerticalScroll(*response_children)

    @on(message_type=Switch.Changed)
    def _add_to_download(self, event: Switch.Changed) -> None:
        switch_id = str(event.switch.parent.id)
        element: EndpointCollapsible = self.query_one(
            selector=f"#{switch_id}"
        ).query_one("EndpointCollapsible")
        playlist: responses.EndpointCollapsible = element.response

        if event.value:
            self.app.download_queue.update({switch_id: playlist})
            self.app.download_table.add_row(
                playlist.title, "wait", key=switch_id
            )
        else:
            self.app.download_queue.pop(switch_id)
            self.app.download_table.remove_row(row_key=switch_id)

    def _watch_collapsed(self, collapsed: bool) -> None:
        if not self.collapsed and not self._is_mounted_response:
            self.mount(self._get_child_container(), after=self._anchor)
        self._is_mounted_response = True
        return super()._watch_collapsed(collapsed)


class BrowseEndpointsWidget(Static):
    """Widget with self.app.start_responses endpoints."""

    def __init__(
        self,
        renderable: str = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.app: YtMusicApp  # define type for self.app for better work IDE
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    # def _set_credentials(self):
    #     user_selector: Select = self.app.query_children("#select_user_widget")

    def compose(self) -> ComposeResult:
        # self._set_credentials()
        # Changed(Select(id="select_user_widget"), "jjjj.txt")
        yield VerticalScroll(
            *[
                EndpointCollapsible(response=response)
                for response in self.app.start_responses
            ],
        )
