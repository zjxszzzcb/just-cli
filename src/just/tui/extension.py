from textual.app import App
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Input, Header, Footer, Label

from just.tui.editor import EditArea


class ExtensionTUI(App):
    """TUI for configuring just extensions"""

    BINDINGS = [
        Binding("ctrl+j", "confirm", "Confirm"),
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    #editor-container {
        height: 70%;
        border: solid green;
    }

    #input-container {
        height: 20%;
        border: solid blue;
        layout: vertical;
    }

    EditArea {
        height: 1fr;
    }

    Input {
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(self):
        super().__init__()
        self.editor = EditArea(id="command-editor")
        self.input = Input(placeholder="Enter command declaration (e.g., just docker ip <container_id>[id:str])",
                           id="command-input")

    def compose(self):
        """Create the UI layout"""
        yield Header()
        yield Container(
            Vertical(
                Label("Command Template Editor:"),
                self.editor,
                id="editor-container"
            ),
            Vertical(
                Label("Command Declaration:"),
                self.input,
                id="input-container"
            ),
            id="button-container"
        )
        yield Footer()

    def action_confirm(self) -> None:
        """Confirm and save the command"""
        self.save_command()

    def action_cancel(self) -> None:
        """Cancel and exit"""
        self.exit()

    def save_command(self) -> None:
        """Save the configured command"""
        command_template = self.editor.text.strip()
        command_declaration = self.input.value.strip()

        if not command_template:
            self.bell()
            return

        # Process the command template and declaration
        print(f"Command Template: {command_template}")
        print(f"Command Declaration: {command_declaration}")

        # Here we would save the command configuration
        # For now, just show a message
        self.bell()
        self.exit()