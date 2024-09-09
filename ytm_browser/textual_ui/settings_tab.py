import functools
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Literal

from textual import on
from textual.containers import Horizontal, Vertical
from textual.validation import Function, ValidationResult
from textual.widget import Widget
from textual.widgets import (
    Button,
    Input,
    Label,
    Markdown,
    Select,
    Static,
    TabPane,
)

from ytm_browser.core import credentials, custom_exceptions
from ytm_browser.textual_ui import modal_screens

if TYPE_CHECKING:
    from ytm_browser.textual_ui.app import YtMusicApp

ID = "settings"
TITLE = "Settings"

WELLCOME_TEXT = """
# Wellcome to YoutubeMusicBrowser
## TODO: Add instructions here
"""


class TypeDownloadDirWidget(Static):
    """Widget for select download dir path."""

    def on_mount(self) -> None:
        self.app: YtMusicApp  # define type for self.app for better work IDE
        self._validation_label = Label(
            "",
            id="validation_result",
        )
        self.mount(
            Horizontal(
                Label(renderable="Download dir", classes="label_text"),
                Vertical(
                    Input(
                        placeholder="files/music (enter a dir path to download music)",
                        validators=[
                            Function(self._is_dir, " It's not dir."),
                        ],
                        classes="width_auto",
                    ),
                    self._validation_label,
                ),
                classes="height_auto",
            ),
        )

    @on(Input.Changed)
    def _show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if isinstance(event.validation_result, ValidationResult):
            if event.validation_result.is_valid:
                self._validation_label.update("")
            else:
                self._validation_label.update(
                    event.validation_result.failure_descriptions[0]
                )

    @on(message_type=Input.Changed)
    def _set_download_dir(self, event: Input.Submitted) -> None:
        self.app.app_paths["download_dir"] = event.value

    def _is_dir(self, typed_path: str) -> bool:
        return Path(typed_path).is_dir()


class UserWidget(Static):
    def __init__(
        self, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.app: YtMusicApp  # define type for self.app for better work IDE

    def select_user_widget(self) -> Select:
        options = self._get_select_widget_content()
        return Select(
            id="select_user_widget",
            options=options["options_list"],
            allow_blank=False,
            value=options["options_list"][-1][1],
            disabled=options["disabled_flag"],
        )

    def add_user_button(self) -> Button:
        return Button(
            label="Add from clipboard",
            variant="warning",
            id="add_auth_file_button",
        )

    def on_mount(self) -> None:
        self.mount(
            Horizontal(
                Label(renderable="Select user", classes="label_text"),
                self.select_user_widget(),
                self.add_user_button(),
                classes="height_auto",
            ),
        )

    @on(Select.Changed)
    def _select_changed(self, event: Select.Changed) -> None:
        selected_value = str(event.value)
        self.app.app_data["credential_file"] = selected_value
        self.app.app_data["auth_data"] = self.credentials_files[selected_value]

    @on(message_type=Button.Pressed, selector="#add_auth_file_button")
    def _add_new_auth_file(self) -> None:
        credentials_raw_data = credentials.read_credentials_from_clipboard()

        def add_credential_file(
            credentials_raw_data: list[str],
            filename: str | Path,
        ) -> None:
            credentials.dump_credentials(
                raw_curl_content=credentials_raw_data,
                target_file=f"{self.app.app_paths['credentials_dir']}/{filename}.txt",
            )
            self._refresh_select_widget()

        pinned_credentials_raw_data = functools.partial(
            add_credential_file,
            credentials_raw_data,
        )

        try:
            credentials.parse_curl_request(credentials_raw_data)
        except custom_exceptions.CredentialsDataError:
            error_message = "Clipboard content does not match cURL request.\nSee the instruction please."
            self.app.push_screen(
                screen=modal_screens.ShowMessageScreen(message=error_message),
            )
        else:
            self.app.push_screen(
                modal_screens.TypeFilenameScreen(),
                pinned_credentials_raw_data,
            )

    def _get_select_widget_content(
        self,
    ) -> dict[Literal["options_list", "disabled_flag"], Any]:
        self.credentials_files = credentials.search_credentials_in_dir(
            dir_path=self.app.app_paths["credentials_dir"],
        )
        if self.credentials_files:
            options_list = tuple(
                (line, line) for line in self.credentials_files
            )
            disabled_flag = False
            # load default auth_data to app (last entry).
            self.app.app_data["auth_data"] = self.credentials_files[
                options_list[-1][1]
            ]
        else:
            options_list = (
                ("Any authfile not found. Please add it.", "notfound"),
            )
            disabled_flag = True
        return {"options_list": options_list, "disabled_flag": disabled_flag}

    def _refresh_select_widget(self) -> None:
        select_user_widget = self.query_one("#select_user_widget")
        if isinstance(select_user_widget, Select):
            select_widget_content = self._get_select_widget_content()
            select_user_widget.set_options(
                select_widget_content["options_list"],
            )
            select_user_widget.disabled = select_widget_content[
                "disabled_flag"
            ]


class SettingsTabPane(TabPane):
    def compose(self) -> Iterable[Widget]:
        with Vertical(id="settings_grid"):
            yield Markdown(WELLCOME_TEXT, classes="height_auto")
            yield UserWidget()
            yield TypeDownloadDirWidget()

        # with Vertical(id="settings_grid"):
