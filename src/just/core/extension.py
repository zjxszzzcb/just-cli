import typer
from typing import List, Optional
from just import create_typer_app, echo


just_ext_cli = create_typer_app()


@just_ext_cli.command(name="add", context_settings={"ignore_unknown_options": True})
def add_extension(
    command: Optional[List[str]] = typer.Argument(None, help="The command to register as a just extension"),
    tui: bool = typer.Option(False, "--tui", help="Launch TUI to configure the command")
):
    """
    Parse and register a command as a just extension.

    Args:
        command: The command to register, e.g., "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef"
        tui: Whether to launch TUI mode
    """
    # If no command provided or TUI mode requested, launch TUI
    if not command or tui:
        launch_tui()
        return

    # The command parts are already parsed correctly thanks to ignore_unknown_options
    command_parts = command

    # Print parsed command for debugging
    print(f"Parsed command: {command_parts}")
    print(f"Original command args: {command}")

    # Here we would continue with further processing of the command
    # For now, just show what we've parsed
    echo.echo(f"Registered command: {' '.join(command_parts)}")



@just_ext_cli.command(name="configure")
def configure_extension():
    ...


def launch_tui():
    """Launch TUI for configuring extension commands"""
    from textual.app import App
    from textual.widgets import Input, Header, Footer, Label
    from textual.containers import Container, Vertical
    from textual.binding import Binding
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
            self.input = Input(placeholder="Enter command declaration (e.g., just docker ip <container_id>[id:str])", id="command-input")

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

    # Launch the TUI app
    app = ExtensionTUI()
    app.run()


def run_just_ext():
    just_ext_cli()
