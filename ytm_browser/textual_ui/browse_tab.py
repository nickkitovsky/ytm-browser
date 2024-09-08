"""Widgets for explore tab."""

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Grid, VerticalScroll
from textual.widgets import Collapsible, Label, Switch

from ytm_browser.core.responses import (
    AbstractResponse,
    EndpointResponse,
    PlaylistResponse,
    registered_responses_types,
)
from ytm_browser.start_endpoints import endpoints

if TYPE_CHECKING:
    from ytm_browser.textual_ui.app import YtMusicApp


class CustomCollapsible(Collapsible):
    """Changebe behavior for default 'Collapsible' for lazy loading child containers."""

    def __init__(
        self,
        response: AbstractResponse,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self.app: YtMusicApp  # define type for self.app for better work IDE
        self.title = response.title
        self._anchor = Label("")
        self.response = response

        super().__init__(
            self._anchor,
            title=self.title,
        )

    def on_mount(self) -> None:
        self._is_mounted_response = False

    def _get_child_container(self) -> Label:
        """Set default child container if the function is not overridden."""
        return Label(renderable="Child Container")

    def _watch_collapsed(self, collapsed: bool) -> None:
        if not self.collapsed and not self._is_mounted_response:
            self.mount(self._get_child_container(), after=self._anchor)
        self._is_mounted_response = True
        return super()._watch_collapsed(collapsed)


class EndpointCollapssible(CustomCollapsible):
    """Endpoint collapsible for views playlists."""

    @on(message_type=Switch.Changed)
    def _add_to_download(self, event: Switch.Changed) -> None:
        switch_id = str(event.switch.parent.id)
        element: CustomCollapsible = self.query_one(
            selector=f"#{switch_id}"
        ).query_one("PlaylistCollapssible")
        playlist: PlaylistResponse = element.response

        if event.value:
            self.app.download_queue.update({switch_id: playlist})
            self.app.download_table.add_row(
                playlist.title, "wait", key=switch_id
            )
        else:
            self.app.download_queue.pop(switch_id)
            self.app.download_table.remove_row(row_key=switch_id)

    def _extract_playlist_id(self, playlist: PlaylistResponse) -> str:
        match playlist.payload:
            case {"playlistId": item_id} | {"videoId": item_id}:
                return f"_{item_id}"
            case _:
                msg = f"Not found id in:\n{playlist.payload}"
                raise AttributeError(msg)

    def _get_child_container(self):
        container = []
        for playlist in self.response_structure.playlists:
            container.append(
                Grid(
                    Switch(animate=True),
                    # PlaylistCollapssible(playlist),
                    # id=self._extract_playlist_id(playlist=playlist),
                    # classes="playlists_grid",
                ),
            )
        return VerticalScroll(*container)
