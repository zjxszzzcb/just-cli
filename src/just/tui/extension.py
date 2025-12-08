from textual.app import App
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Header, Footer, Label, TextArea

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
        height: 60%;
        border: solid green;
    }

    #input-container {
        height: 30%;
        border: solid blue;
        layout: vertical;
    }

    #main-container {
        height: 90%;
    }

    #hint-container {
        height: 8%;
        border: solid yellow;
        padding: 1;
    }

    EditArea {
        height: 1fr;
    }

    Input {
        width: 100%;
        margin: 1 0;
    }

    Label {
        margin: 1 0 0 0;
        text-style: bold;
    }

    .help-text {
        color: gray;
        margin: 0 0 0 1;
        text-style: italic;
    }

    .syntax-hint {
        margin: 0 0 0 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.editor = EditArea(id="command-editor")
        self.template_input = Input(placeholder="Enter command template (e.g., curl --data-raw 'domain=<DOMAIN>' <URL>)",
                                   id="template-input")
        self.declaration_input = Input(placeholder="Enter command declaration (e.g., just dnslog new <URL>[url:str] --domain <DOMAIN>[domain:str=default#help])",
                                      id="declaration-input")

    def compose(self):
        """Create the UI layout"""
        yield Header()
        yield Container(
            Vertical(
                Label("Command Template:"),
                self.editor,
                id="editor-container"
            ),
            Vertical(
                Label("Command Declaration:"),
                Label("Format: just <command> [ARGUMENT:type=default#help] [--option VALUE:type#help]",
                      classes="help-text"),
                Label("Examples:", classes="help-text"),
                Label("  just docker inspect-container CONTAINER_ID:str#container identifier",
                      classes="help-text"),
                Label("  just api-call endpoint:str=https://api.example.com --method GET:type=str",
                      classes="help-text"),
                Label("✓ Valid: letters, numbers, underscores", classes="syntax-hint"),
                Label("✗ Special chars: -, /, . will be auto-replaced with _", classes="syntax-hint"),
                Label("✓ Numeric: commands like '123' become 'num_123'", classes="syntax-hint"),
                self.declaration_input,
                id="input-container"
            ),
            id="main-container"
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
        # Use editor text if available, otherwise use template input
        command_template = self.editor.text.strip() or self.template_input.value.strip()
        command_declaration = self.declaration_input.value.strip()

        if not command_template:
            self.bell()
            return

        # Show syntax hints in terminal
        print("\n" + "="*60)
        print("Command Declaration Syntax Hints:")
        print("  Format: just <command> [ARGUMENT:type=default#help] [--option VALUE:type#help]")
        print("")
        print("  Examples:")
        print("    just docker inspect-container CONTAINER_ID:str#container identifier")
        print("    just api-call endpoint:str=https://api.example.com --method GET:type=str")
        print("")
        print("  ✓ Valid: letters, numbers, underscores")
        print("  ✗ Special chars: -, /, . will be auto-replaced with _")
        print("  ✓ Numeric: commands like '123' become 'num_123'")
        print("="*60 + "\n")

        # Process the command template and declaration
        print(f"Command Template: {command_template}")
        print(f"Command Declaration: {command_declaration}")

        # Import and use the extension creation function
        try:
            from just.core.extension.generator import generate_extension_script
            import shlex

            # Parse the declaration into a list of arguments
            just_commands = shlex.split(command_declaration)

            # Create the extension
            generate_extension_script(command_template, just_commands)
            print(f"Extension created successfully!")
        except Exception as e:
            print(f"Error creating extension: {e}")

        # Show success message and exit
        self.bell()
        self.exit()