from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class TypeFilenameScreen(ModalScreen):
    """Screen with a dialog to enter filename."""

    BINDINGS = [("escape", "pop_screen", "Close")]

    def compose(self) -> ComposeResult:
        self._filename_input = Input(placeholder="Enter authfile name", id="filename_input", classes="center_element")
        yield Grid(
            self._filename_input,
            Button("Ok", variant="success", id="ok"),
            Button("Cancel", variant="primary", id="cancel"),
            id="modal_dialog",
            classes="height_auto",
        )

    @on(message_type=Input.Submitted, selector="#filename_input")
    def press_enter_on_input(self) -> None:
        self.dismiss(self._filename_input.value)

    @on(message_type=Button.Pressed, selector="#ok")
    def press_ok(self) -> None:
        self.dismiss(self._filename_input.value)

    @on(message_type=Button.Pressed, selector="#cancel")
    def press_cancel(self) -> None:
        self.app.pop_screen()


class ShowMessageScreen(ModalScreen):
    """Parent class for show message screen and a 'ok' button."""

    BINDINGS = [("escape", "pop_screen", "Close")]

    def __init__(
        self, message: str = "", name: str | None = None, id: str | None = None, classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.message = message
        self.message_label = Label(self.message, classes="center_element")

    def compose(self) -> ComposeResult:
        yield Grid(
            self.message_label,
            Button("Ok", variant="success", classes="center_element", id="ok"),
            id="modal_dialog",
            classes="height_auto",
        )

    @on(message_type=Button.Pressed, selector="#ok")
    def press_ok(self) -> None:
        self.app.pop_screen()
