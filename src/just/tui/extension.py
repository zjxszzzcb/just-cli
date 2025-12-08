from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal, VerticalScroll, Grid
from textual.widgets import Input, Header, Footer, Label, Button, Select, Static
from textual.reactive import reactive

from just.tui.editor import EditArea
from rich.markup import escape

class ComponentDisplay(Horizontal):
    """Widget to display a configured component in the list"""
    def __init__(self, value: str, label: str, data: dict, id: str = None):
        super().__init__(id=id, classes="component-item")
        self.value_str = value
        self.label_str = label
        self.data = data

    def compose(self) -> ComposeResult:
        yield Label(self.render_label(), classes="component-label")
        yield Button("✕", id="remove", variant="error", classes="remove-btn")

    def on_click(self, event) -> None:
        self.app.action_edit_component(self)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "remove":
            event.stop() 
            self.app.action_remove_component(self)

    def update_display(self, value: str, label: str, data: dict) -> None:
        self.value_str = value
        self.label_str = label
        self.data = data
        self.query_one(".component-label", Label).update(self.render_label())

    def render_label(self) -> str:
        """Generate Rich markup for the component label"""
        if self.label_str == "Subcommand":
            name = self.data.get("name", "???")
            # Pale Yellow (Khaki)
            return f"[bold black on #F0E68C] CMD [/] [bold #F0E68C] {name} [/]"
        elif self.label_str == "Argument":
            ph = self.data.get("placeholder", "???")
            typ = self.data.get("type", "str")
            # Pale Green
            return f"[bold black on #90EE90] ARG [/] [bold #90EE90] {ph} [/] [dim]({typ})[/]"
        elif self.label_str == "Option":
            flag = self.data.get("flag", "???")
            var = self.data.get("variable", "")
            # Pale Pink
            return f"[bold black on #FFB6C1] OPT [/] [bold #FFB6C1] {flag} [/] [dim]{var}[/]"
        return f"[{self.label_str}] {self.value_str}"

# Forms remain largely the same, but CSS needs update for components-list items
class SubcommandForm(Container):
    def compose(self) -> ComposeResult:
        yield Label("Add Subcommand", classes="form-header")
        yield Input(placeholder="Subcommand Name (e.g. new)", id="sub-name")
        with Horizontal(classes="form-buttons"):
            yield Button("Confirm", variant="primary", id="confirm")

class ArgumentForm(Container):
    def compose(self) -> ComposeResult:
        yield Label("Add Argument", classes="form-header")
        yield Input(placeholder="Placeholder Name (e.g. URL)", id="arg-placeholder")
        with Container(classes="split-row"):
            yield Input(placeholder="Variable Name (optional)", id="arg-var")
            yield Select([("str", "str"), ("int", "int"), ("bool", "bool"), ("float", "float")], value="str", id="arg-type", allow_blank=False)
        yield Input(placeholder="Default Value (optional)", id="arg-default")
        yield Input(placeholder="Help Text (optional)", id="arg-help")
        with Horizontal(classes="form-buttons"):
            yield Button("Confirm", variant="primary", id="confirm")

class OptionForm(Container):
    def compose(self) -> ComposeResult:
        yield Label("Add Option", classes="form-header")
        with Container(classes="split-row"):
            yield Input(placeholder="Flag (e.g. -f or --force)", id="opt-flag")
            yield Input(placeholder="Value Placeholder (optional)", id="opt-val-placeholder")
        with Container(classes="split-row"):
            yield Input(placeholder="Variable Name (optional)", id="opt-var")
            yield Select([("str", "str"), ("int", "int"), ("bool", "bool"), ("float", "float")], value="str", id="opt-type", allow_blank=False)
        yield Input(placeholder="Default Value (optional)", id="opt-default")
        yield Input(placeholder="Help Text (optional)", id="opt-help")
        with Horizontal(classes="form-buttons"):
            yield Button("Confirm", variant="primary", id="confirm")

# SaveScreen ... (Unchanged)
from textual.screen import ModalScreen

class SaveScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Save and generate extension?", id="question"),
            Horizontal(
                Button("Yes", variant="primary", id="yes"),
                Button("No", variant="error", id="no"),
                id="buttons",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

class ExtensionTUI(App):
    """TUI for configuring just extensions"""

    CSS = """
    Screen {
        layout: vertical;
        padding: 1;
    }
    
    /* ... existing CSS ... */

    /* Component List Styling */
    .component-item {
        height: 3;
        border: solid gray;
        margin: 0;
        padding: 0 1;
        background: $surface;
        align: left middle;
    }
    
    .component-item:hover {
        background: $surface-lighten-1;
        border: solid #00BFFF;
    }
    
    .component-item.editing {
        border: solid white;
        background: $surface-lighten-1;
    }

    .component-item.editing-sub {
        border: solid #F0E68C;
        background: $surface-lighten-1;
    }

    .component-item.editing-arg {
        border: solid #90EE90;
        background: $surface-lighten-1;
    }

    .component-item.editing-opt {
        border: solid #FFB6C1;
        background: $surface-lighten-1;
    }
    
    .component-label {
        width: 1fr;
        content-align: left middle;
        height: 100%;
    }
    

    
    /* Save Modal */
    SaveScreen {
        align: center middle;
    }

    #dialog {
        padding: 0 1;
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }

    #question {
        height: 1fr;
        width: 100%;
        content-align: center middle;
    }
    
    #buttons {
        height: 5;
        width: 100%;
        align: center middle;
    }
    
    #buttons Button {
        margin: 0 2;
    }

    #editor-container {
        height: 8;
        border: round $primary;
        margin-bottom: 0;
        background: $surface;
    }
    
    TextArea:focus {
        border: solid #00BFFF;
    }

    /* Button Colors handled down below */
    
    #preview-section {
        height: auto;
        border-bottom: solid gray;
        padding-bottom: 0;
        margin-bottom: 1;
        background: $surface-darken-1;
    }
    
    #preview-label {
        background: $surface-darken-1;
        padding: 0 1;
        width: 100%;
        height: 1;
    }

    #main-work-area {
        layout: horizontal;
        height: 1fr;
        margin-top: 1;
    }
    
    #list-column {
        width: 50%;
        height: 100%;
        border: round gray;
        margin-right: 1;
    }
    
    #form-column {
        width: 50%;
        height: 100%;
        padding-left: 1;
        overflow-y: scroll;
        scrollbar-color: $primary $surface;
        border: round gray;
    }

    #form-column > Container {
        height: auto;
    }

    #form-placeholder {
        height: auto;
    }
    
    SubcommandForm, ArgumentForm, OptionForm {
        height: auto;
        margin-bottom: 2;
    }

    #controls {
        height: auto;
        margin-bottom: 0;
        margin-left: 1;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
    }
    
    #components-list {
        height: 1fr;
        border: solid gray;
        background: $surface;
    }

    .form-header {
        text-style: bold;
        margin-bottom: 1;
        width: 100%;
        text-align: center;
    }
    
    .form-buttons {
        align: center middle;
        margin-top: 1;
        height: auto;
    }
    
    #controls Button {
        border: none;
        height: 3;
        width: auto;
        min-width: 16;
    }

    /* Button Colors */
    #btn-add-sub:hover, #btn-add-sub:focus, #btn-add-sub.active {
        background: #F0E68C;
        color: black;
    }
    
    #btn-add-arg:hover, #btn-add-arg:focus, #btn-add-arg.active {
        background: #90EE90;
        color: black;
    }
    
    #btn-add-opt:hover, #btn-add-opt:focus, #btn-add-opt.active {
        background: #FFB6C1;
        color: black;
    }
    
    .remove-btn {
        width: 4;
        min-width: 4;
        height: 1;
        padding: 0;
        border: none;
        content-align: center middle;
        text-style: bold;
        background: transparent;
        color: #FF5555;
    }

    .remove-btn:hover {
        background: #FF5555;
        color: white;
    }
    
    Input {
        margin-bottom: 1;
        height: 3;
        border: solid gray;
    }

    Input:hover, Input:focus {
        border: solid #00BFFF;
    }

    Select {
        margin-bottom: 1;
        height: 3;
        border: none;
    }

    Select > SelectCurrent {
        border: solid gray;
    }

    Select:focus > SelectCurrent, Select:hover > SelectCurrent {
        border: solid #00BFFF;
    }
    
    .split-row {
        layout: grid;
        grid-size: 2;
        grid-gutter: 1;
        height: 3;
        margin-bottom: 1;
    }
    
    .split-row Input, .split-row Select {
        margin-bottom: 0;
    }
    
    #confirm {
        width: 100%;
        height: 3;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "request_save", "Save & Exit"),
        Binding("escape", "quit_app", "Quit"),
    ]

    preview_text = reactive("just")

    def __init__(self):
        super().__init__()
        self.editor = EditArea(id="command-editor")
        self.components_container = VerticalScroll(id="components-list")
        self.form_container = Container(id="form-placeholder") # Empty initially
        self.preview_label = Label("just", id="preview-label")
        self.editing_component = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(Label("Command Template:", classes="label"), self.editor, id="editor-container")
        yield Container(Label("Command Preview:", classes="label"), self.preview_label, id="preview-section")
        yield Container(
            Vertical(
                Container(
                    Button("Add Subcommand", id="btn-add-sub"),
                    Button("Add Argument", id="btn-add-arg"),
                    Button("Add Option", id="btn-add-opt"),
                    id="controls"
                ),
                self.components_container,
                id="list-column"
            ),
            VerticalScroll(self.form_container, id="form-column"),
            id="main-work-area"
        )
        yield Footer()

    def action_request_save(self) -> None:
        def check_save(should_save: bool) -> None:
            if should_save:
                self.action_save_and_exit()
        self.push_screen(SaveScreen(), check_save)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        
        if btn_id in ["btn-add-sub", "btn-add-arg", "btn-add-opt"]:
            self.clear_editing_state()
            self.update_active_button(btn_id)
            
            if btn_id == "btn-add-sub":
                self.mount_form(SubcommandForm())
            elif btn_id == "btn-add-arg":
                self.mount_form(ArgumentForm())
            elif btn_id == "btn-add-opt":
                self.mount_form(OptionForm())
            
        elif btn_id == "confirm":
            self.handle_form_confirm()

    def update_active_button(self, active_id: str) -> None:
        for bid in ["btn-add-sub", "btn-add-arg", "btn-add-opt"]:
            try:
                btn = self.query_one(f"#{bid}", Button)
                if bid == active_id:
                    btn.add_class("active")
                else:
                    btn.remove_class("active")
            except:
                pass

    def mount_form(self, form_widget) -> None:
        self.form_container.remove_children()
        self.form_container.mount(form_widget)
        # Auto-focus the first input to save a click and fix focus styling
        try:
            form_widget.query("Input").first().focus()
        except:
            pass

    def clear_editing_state(self) -> None:
        if self.editing_component:
            self.editing_component.remove_class("editing")
            self.editing_component.remove_class("editing-sub")
            self.editing_component.remove_class("editing-arg")
            self.editing_component.remove_class("editing-opt")
            self.editing_component = None

    def action_edit_component(self, component: ComponentDisplay) -> None:
        self.clear_editing_state()
        
        self.editing_component = component
        component.add_class("editing")
        
        data = component.data
        type_ = component.label_str
        
        if type_ == "Subcommand":
            self.update_active_button("btn-add-sub")
            component.add_class("editing-sub")
            f = SubcommandForm()
            self.mount_form(f)
            f.query_one("#sub-name", Input).value = data["name"]
        
        elif type_ == "Argument":
            self.update_active_button("btn-add-arg")
            component.add_class("editing-arg")
            f = ArgumentForm()
            self.mount_form(f)
            f.query_one("#arg-placeholder", Input).value = data["placeholder"]
            f.query_one("#arg-var", Input).value = data["variable"]
            f.query_one("#arg-type", Select).value = data["type"]
            f.query_one("#arg-default", Input).value = data["default"]
            f.query_one("#arg-help", Input).value = data["help"]
            
        elif type_ == "Option":
            self.update_active_button("btn-add-opt")
            component.add_class("editing-opt")
            f = OptionForm()
            self.mount_form(f)
            f.query_one("#opt-flag", Input).value = data["flag"]
            f.query_one("#opt-val-placeholder", Input).value = data["placeholder"]
            f.query_one("#opt-var", Input).value = data["variable"]
            f.query_one("#opt-type", Select).value = data["type"]
            f.query_one("#opt-default", Input).value = data["default"]
            f.query_one("#opt-help", Input).value = data["help"]
            
    def action_remove_component(self, component: ComponentDisplay) -> None:
        if component == self.editing_component:
            self.clear_editing_state()
        component.remove()
        self.update_preview(ignore_component=component)

    def validate_name(self, name: str, field_name: str) -> bool:
        """Validate that name contains only alphanumeric, _, - and is not purely numeric."""
        import re
        if not name:
            self.notify(f"{field_name} cannot be empty.", severity="error")
            return False
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            self.notify(f"{field_name} must contain only letters, numbers, underscores, or hyphens.", severity="error")
            return False
        if name.isdigit():
            self.notify(f"{field_name} cannot be purely numeric.", severity="error")
            return False
        return True

    def handle_form_confirm(self) -> None:
        form = self.form_container.query_children().first()
        data = {}
        val = ""
        ctype = ""

        if isinstance(form, SubcommandForm):
            name = form.query_one("#sub-name", Input).value.strip()
            if self.validate_name(name, "Subcommand Name"):
                data = {"name": name}
                val = name
                ctype = "Subcommand"

        elif isinstance(form, ArgumentForm):
            p = form.query_one("#arg-placeholder", Input).value.strip()
            v = form.query_one("#arg-var", Input).value.strip()
            t = form.query_one("#arg-type", Select).value
            d = form.query_one("#arg-default", Input).value.strip()
            h = form.query_one("#arg-help", Input).value.strip()
            
            # Helper to check variable name only if provided
            valid_var = True
            if v:
                valid_var = self.validate_name(v, "Variable Name")

            if p and valid_var:
                # Placeholder usually uppercase but can be flexible, ensure placeholder isn't empty
                if not p:
                     self.notify("Placeholder cannot be empty.", severity="error")
                else:
                    data = {"placeholder": p, "variable": v, "type": t, "default": d, "help": h}
                    ctype = "Argument"
                    val = f"<{p}>"
                    if v or t != "str" or d or h:
                        val += "["
                        # If variable is not provided, we derive it from placeholder, usually safe but let's be lenient
                        var_val = v if v else p.lower().replace("-", "_")
                        val += var_val
                        val += f":{t}"
                        if d: val += f"={d}"
                        if h: val += f"#{h}"
                        val += "]"

        elif isinstance(form, OptionForm):
            f = form.query_one("#opt-flag", Input).value.strip()
            ph = form.query_one("#opt-val-placeholder", Input).value.strip()
            v = form.query_one("#opt-var", Input).value.strip()
            t = form.query_one("#opt-type", Select).value
            d = form.query_one("#opt-default", Input).value.strip()
            h = form.query_one("#opt-help", Input).value.strip()
            
            valid_var = True
            if v:
                valid_var = self.validate_name(v, "Variable Name")
            
            if f and valid_var:
                if not f.startswith("-"):
                     self.notify("Flag must start with - or --", severity="error")
                else:
                    data = {"flag": f, "placeholder": ph, "variable": v, "type": t, "default": d, "help": h}
                    ctype = "Option"
                    val = f"{f}"
                    # Variable validation logic
                    var_name = v if v else f.lstrip("-").replace("-", "_")
                    
                    if t == "bool":
                        val += "["
                        val += var_name
                        val += ":bool"
                        if d: val += f"={d}"
                        if h: val += f"#{h}"
                        val += "]"
                    else:
                        val_ph = (ph if ph else (v if v else "VALUE")).upper()
                        val += f" {val_ph}["
                        val += var_name
                        val += f":{t}"
                        if d: val += f"={d}"
                        if h: val += f"#{h}"
                        val += "]"

        if val and ctype:
            if self.editing_component:
                self.editing_component.update_display(val, ctype, data)
                self.clear_editing_state()
            else:
                self.add_component(val, ctype, data)
            
            self.form_container.remove_children()
            self.update_preview()
            self.editor.focus() # Return focus to easy typing

    def add_component(self, value: str, label: str, data: dict) -> None:
        self.components_container.mount(ComponentDisplay(value, label, data))
        self.update_preview()

    def update_preview(self, ignore_component=None) -> None:
        parts = ["just"]
        for widget in self.components_container.children:
             if isinstance(widget, ComponentDisplay):
                 if widget == ignore_component:
                     continue
                 v = widget.value_str
                 color = "white"
                 if widget.label_str == "Subcommand": color = "#F0E68C"
                 elif widget.label_str == "Argument": color = "#90EE90"
                 elif widget.label_str == "Option": color = "#FFB6C1"
                 
                 parts.append(f"[{color}]{escape(v)}[/{color}]")
        
        self.preview_text = " ".join(parts)
        self.preview_label.update(self.preview_text)

    def action_save_and_exit(self) -> None:
        # Note: Need raw text for command generation, strip markup
        import re
        
        # Validate Command Template
        command_template = self.editor.text.strip()
        if not command_template:
            self.notify("Command template cannot be empty.", severity="error")
            return

        # Validate Components
        has_components = False
        parts = ["just"]
        for widget in self.components_container.children:
             if isinstance(widget, ComponentDisplay):
                 parts.append(widget.value_str)
                 has_components = True
        
        if not has_components:
            self.notify("Command list cannot be empty. Add at least one subcommand, argument, or option.", severity="error")
            return

        raw_cmd = " ".join(parts)
        folder_declaration = raw_cmd
        command_declaration = folder_declaration.replace("just ", "", 1).strip()

        try:
            from just.core.extension.generator import generate_extension_script
            import shlex
            
            just_commands = shlex.split(command_declaration)
            generate_extension_script(command_template, just_commands)
            self.notify("Extension created successfully!", severity="information")
            self.set_timer(1.0, self.exit)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")