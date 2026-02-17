# Textual Quick Reference Guide

A quick reference for common patterns and operations in Textual TUI applications.

## Table of Contents

1. [Basic App Template](#basic-app-template)
2. [Widget Lifecycle](#widget-lifecycle)
3. [CSS Cheat Sheet](#css-cheat-sheet)
4. [Common Patterns](#common-patterns)
5. [Testing Templates](#testing-templates)
6. [Debugging Commands](#debugging-commands)

---

## Basic App Template

### Minimal App

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hello, Textual!")
        yield Footer()

if __name__ == "__main__":
    MyApp().run()
```

### Multi-Screen App

```python
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button

class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Button("Go to Settings", id="settings-btn")
        yield Footer()

    def on_button_pressed(self) -> None:
        self.app.push_screen("settings")

class SettingsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Button("Back", id="back-btn")
        yield Footer()

    def on_button_pressed(self) -> None:
        self.app.pop_screen()

class MyApp(App):
    SCREENS = {
        "main": MainScreen,
        "settings": SettingsScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("main")

if __name__ == "__main__":
    MyApp().run()
```

### App with External CSS

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MyApp(App):
    CSS_PATH = "app.tcss"  # External CSS file

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Styled content", id="content")
        yield Footer()

if __name__ == "__main__":
    MyApp().run()
```

---

## Widget Lifecycle

### Key Lifecycle Methods

```python
from textual.widget import Widget

class MyWidget(Widget):
    def __init__(self, **kwargs) -> None:
        """Called when widget is created."""
        super().__init__(**kwargs)
        # Don't modify reactive attributes here!
        # Use set_reactive() instead

    def compose(self) -> ComposeResult:
        """Called to build child widgets."""
        yield ChildWidget()

    def on_mount(self) -> None:
        """Called after widget is mounted to DOM."""
        # Safe to modify reactive attributes
        # Initialize connections, start timers
        self.set_interval(1, self.update_data)

    def on_unmount(self) -> None:
        """Called before widget is removed."""
        # Cleanup: close connections, cancel timers
        pass

    def on_show(self) -> None:
        """Called when widget becomes visible."""
        pass

    def on_hide(self) -> None:
        """Called when widget becomes hidden."""
        pass

    def on_resize(self, event: events.Resize) -> None:
        """Called when widget size changes."""
        pass
```

### Event Handlers

```python
from textual.widgets import Button, Input

class MyWidget(Widget):
    # Method naming: on_<widget>_<event>
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle any button press in this widget."""
        button = event.button
        self.log(f"Button {button.id} pressed")

    # Or handle specific widget
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        value = event.value
        await self.validate_input(value)

    # Generic event handler
    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "escape":
            self.app.exit()
```

---

## CSS Cheat Sheet

### Layout Properties

```css
/* Docking - fix widget position */
#header {
    dock: top;
    height: 3;
}

#sidebar {
    dock: left;
    width: 30;
}

#footer {
    dock: bottom;
    height: 1;
}

/* Flexible sizing with FR units */
#content {
    width: 1fr;   /* Fill available space */
    height: 1fr;
}

#left {
    width: 1fr;   /* 1 part */
}

#right {
    width: 2fr;   /* 2 parts (twice as wide) */
}

/* Alignment */
Screen {
    align: center middle;  /* horizontal vertical */
}

#widget {
    text-align: center;           /* Align text lines */
    content-align: center middle; /* Align content block */
}

/* Grid layout */
#grid-container {
    layout: grid;
    grid-size: 3 2;           /* columns rows */
    grid-columns: 1fr 2fr 1fr;
    grid-rows: auto auto;
    grid-gutter: 1 2;         /* vertical horizontal */
}

#wide-cell {
    column-span: 2;
}
```

### Visual Properties

```css
/* Colors - use theme variables */
Button {
    background: $primary;
    color: $text;
    border: solid $accent;
}

/* Spacing */
.container {
    padding: 1 2;    /* vertical horizontal */
    margin: 1;       /* all sides */
}

/* Borders */
#panel {
    border: solid blue;
    border-top: heavy green;
    border-title-align: center;
}

/* Display */
.hidden {
    display: none;
}

.visible {
    display: block;
}

/* Opacity */
.disabled {
    opacity: 0.5;
}

/* Scrolling */
#scrollable {
    overflow-y: scroll;
    overflow-x: hidden;
}
```

### Selectors & Pseudo-classes

```css
/* Type selector */
Button { }

/* ID selector */
#submit-button { }

/* Class selector */
.primary-button { }

/* Descendant */
#dialog Button { }

/* Child */
#sidebar > Button { }

/* Pseudo-classes */
Button:hover { }
Button:focus { }
Input:disabled { }
Widget:dark { }     /* Dark theme */
Widget:light { }    /* Light theme */

/* Nesting */
Button {
    background: blue;

    &:hover {
        background: lightblue;
    }

    &.danger {
        background: red;
    }
}
```

### Theme Color Variables

```css
/* Primary semantic colors */
$primary
$secondary
$accent
$warning
$error
$success

/* Background colors */
$background
$surface
$panel
$boost

/* Text colors */
$text
$text-muted
$text-disabled

/* Color variations */
$primary-lighten-1
$primary-lighten-2
$primary-lighten-3
$primary-darken-1
$primary-darken-2
$primary-darken-3
$primary-muted
```

---

## Common Patterns

### Reactive Attributes

```python
from textual.reactive import reactive

class Counter(Widget):
    # Basic reactive
    count = reactive(0)

    def render(self) -> str:
        return f"Count: {self.count}"

    # With validation
    age = reactive(0)

    def validate_age(self, value: int) -> int:
        return max(0, min(value, 120))

    # With watcher
    status = reactive("idle")

    def watch_status(self, old: str, new: str) -> None:
        if new == "error":
            self.add_class("error-state")

    # Computed property
    doubled = reactive(0)

    def compute_doubled(self) -> int:
        return self.count * 2

    # With recompose
    mode = reactive("list", recompose=True)

    def compose(self) -> ComposeResult:
        if self.mode == "list":
            yield ListView()
        else:
            yield GridView()
```

### Custom Messages

```python
from textual.message import Message

class MyWidget(Widget):
    class Updated(Message):
        """Posted when widget updates."""
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    def update_value(self, value: str) -> None:
        self.value = value
        self.post_message(self.Updated(value))

# Parent handles the message
class ParentWidget(Widget):
    def on_my_widget_updated(self, message: MyWidget.Updated) -> None:
        self.log(f"Widget updated: {message.value}")
```

### Actions and Key Bindings

```python
class MyApp(App):
    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    def action_save(self) -> None:
        """Save action - callable from anywhere."""
        self.save_data()

    def action_help(self) -> None:
        """Show help screen."""
        self.push_screen("help")

# Widget-specific bindings
class MyWidget(Widget):
    BINDINGS = [
        ("enter", "select", "Select"),
        ("escape", "cancel", "Cancel"),
    ]

    def action_select(self) -> None:
        self.log("Selected!")

    def action_cancel(self) -> None:
        self.log("Cancelled!")
```

### Workers for Async Operations

```python
from textual.worker import work

class MyWidget(Widget):
    @work(exclusive=True)  # Cancel previous if still running
    async def load_data(self) -> None:
        """Run async operation without blocking UI."""
        data = await fetch_from_api()
        self.display_data(data)

    @work(thread=True)  # Run in thread for CPU-intensive work
    def process_large_file(self, filename: str) -> None:
        """Process file in background thread."""
        result = heavy_computation(filename)
        self.call_from_thread(self.display_result, result)

    # Call worker
    def on_button_pressed(self) -> None:
        self.load_data()  # Don't await - runs in background
```

### Modal Dialogs

```python
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal

class ConfirmDialog(ModalScreen[bool]):
    """Type-safe confirmation dialog."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static(self.message)
            with Horizontal():
                yield Button("Yes", id="yes", variant="primary")
                yield Button("No", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

# Usage
class MyApp(App):
    def action_delete(self) -> None:
        def check_confirm(confirmed: bool) -> None:
            if confirmed:
                self.delete_item()

        self.push_screen(
            ConfirmDialog("Are you sure?"),
            check_confirm
        )
```

### Data Binding

```python
class ParentWidget(Widget):
    value = reactive(0)

    def compose(self) -> ComposeResult:
        child = ChildWidget()
        # Bind child's display to parent's value
        child.data_bind(self, display="value")
        yield child

class ChildWidget(Widget):
    display = reactive(0)

    def render(self) -> str:
        return f"Value: {self.display}"
```

### Timers and Intervals

```python
class MyWidget(Widget):
    def on_mount(self) -> None:
        # Run once after 5 seconds
        self.set_timer(5, self.delayed_action)

        # Run every 1 second
        self.set_interval(1, self.periodic_update)

    def delayed_action(self) -> None:
        self.log("Timer fired!")

    def periodic_update(self) -> None:
        self.log("Updating...")
```

### Query Widgets

```python
class MyWidget(Widget):
    def find_widgets(self) -> None:
        # Get one widget by ID
        button = self.query_one("#submit", Button)

        # Get one widget by type
        header = self.query_one(Header)

        # Get multiple widgets
        buttons = self.query("Button")

        # Refinement
        first_button = self.query("Button").first()
        last_button = self.query("Button").last()

        # Filter
        enabled = self.query("Button").filter(".enabled")

        # Exclude
        not_disabled = self.query("Button").exclude(".disabled")

        # Iterate
        for button in self.query("Button"):
            button.disabled = True
```

### Container Layouts

```python
from textual.containers import (
    Vertical,
    Horizontal,
    Grid,
    Center,
    Container,
)

class MyScreen(Screen):
    def compose(self) -> ComposeResult:
        # Vertical stack
        with Vertical():
            yield Widget1()
            yield Widget2()

        # Horizontal row
        with Horizontal():
            yield Widget3()
            yield Widget4()

        # Grid
        with Grid():
            yield Widget5()
            yield Widget6()
            yield Widget7()

        # Center
        with Center():
            yield CenteredWidget()
```

---

## Testing Templates

### Basic Test

```python
import pytest
from my_app import MyApp

@pytest.mark.asyncio
async def test_app_loads():
    """Test that app loads successfully."""
    app = MyApp()
    async with app.run_test() as pilot:
        # App is running
        assert app.is_running
```

### Test User Interaction

```python
@pytest.mark.asyncio
async def test_button_click():
    """Test button click interaction."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Click button by ID
        await pilot.click("#submit")

        # Wait for messages to process
        await pilot.pause()

        # Assert state changed
        assert app.query_one("#status").renderable == "Submitted"
```

### Test Keyboard Input

```python
@pytest.mark.asyncio
async def test_keyboard_navigation():
    """Test keyboard navigation."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Press keys
        await pilot.press("tab")
        await pilot.pause()

        # Check focus
        assert app.focused.id == "first-input"

        # Type text
        await pilot.press("h", "e", "l", "l", "o")
        await pilot.pause()

        # Verify input
        assert app.query_one("#first-input").value == "hello"
```

### Test Form Input

```python
@pytest.mark.asyncio
async def test_form_submission():
    """Test form with multiple inputs."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Fill out form
        app.query_one("#name").value = "Alice"
        app.query_one("#email").value = "alice@example.com"

        # Submit
        await pilot.click("#submit")
        await pilot.pause()

        # Verify
        assert app.user_data["name"] == "Alice"
        assert app.user_data["email"] == "alice@example.com"
```

### Test Screen Navigation

```python
@pytest.mark.asyncio
async def test_screen_navigation():
    """Test switching between screens."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Start on main screen
        assert app.screen.name == "main"

        # Navigate to settings
        app.push_screen("settings")
        await pilot.pause()

        assert app.screen.name == "settings"

        # Go back
        app.pop_screen()
        await pilot.pause()

        assert app.screen.name == "main"
```

### Test Reactive Updates

```python
@pytest.mark.asyncio
async def test_reactive_update():
    """Test reactive attribute updates."""
    app = MyApp()
    async with app.run_test() as pilot:
        widget = app.query_one(Counter)

        # Update reactive
        widget.count = 5
        await pilot.pause()

        # Check render
        assert "Count: 5" in str(widget.render())
```

### Test with Custom Size

```python
@pytest.mark.asyncio
async def test_responsive_layout():
    """Test layout at different screen sizes."""
    app = MyApp()

    # Small screen
    async with app.run_test(size=(40, 20)) as pilot:
        assert app.query_one("#sidebar").has_class("compact")

    # Large screen
    async with app.run_test(size=(120, 40)) as pilot:
        assert not app.query_one("#sidebar").has_class("compact")
```

### Test Snapshot (Optional)

```python
async def test_ui_snapshot(snap_compare):
    """Test visual appearance."""
    assert await snap_compare("path/to/app.py")

async def test_ui_after_interaction(snap_compare):
    """Test appearance after interaction."""
    assert await snap_compare(
        "path/to/app.py",
        press=["tab", "enter"],
        terminal_size=(100, 30),
    )
```

---

## Debugging Commands

### Development Console

**Terminal 1 - Start console:**
```bash
textual console
```

**Terminal 2 - Run app:**
```bash
textual run --dev my_app.py
```

**Console options:**
```bash
# Verbose mode (show events)
textual console -v

# Exclude specific events
textual console -x EVENT

# Custom port
textual console --port 7777
```

### In-App Logging

```python
from textual import log

class MyWidget(Widget):
    def on_button_pressed(self) -> None:
        # Log to console
        log("Button pressed!")
        log("Current state:", self.state)
        log(locals())  # Log all local variables

        # Log widget tree
        log(self.tree)

        # Log queries
        log("Buttons:", self.query("Button"))
```

### Screenshots

```bash
# Automatic screenshot after 5 seconds
textual run --screenshot 5 my_app.py

# Or press Ctrl+S in dev mode
textual run --dev my_app.py
```

### Live CSS Editing

```bash
# Dev mode with auto-reload
textual run --dev my_app.py

# Edit .tcss files and see changes immediately
```

### Visual Debugging

```css
/* Add temporary borders to see layout */
* {
    border: solid red;
}

/* Or specific widgets */
.debug {
    border: solid yellow;
}
```

### Python Debugger

```python
async def on_button_pressed(self) -> None:
    breakpoint()  # Start Python debugger
    # Use pdb commands:
    # n - next line
    # s - step into
    # c - continue
    # p <var> - print variable
    await self.some_action()
```

### Run Textual Apps

```bash
# Basic run
textual run app.py

# Dev mode (live reload, screenshots)
textual run --dev app.py

# Custom size
textual run --size 80x24 app.py

# Screenshot after N seconds
textual run --screenshot 5 app.py
```

---

## Useful Built-in Widgets

### Input & Selection
- `Button` - clickable button
- `Checkbox` - checkbox input
- `Input` - single-line text input
- `MaskedInput` - formatted input (phone, credit card)
- `RadioButton`, `RadioSet` - radio button group
- `Select` - dropdown selection
- `SelectionList` - multi-select list
- `Switch` - on/off toggle
- `TextArea` - multi-line text editor with syntax highlighting

### Display
- `Label` - text label
- `Static` - static text with caching
- `Pretty` - pretty-print Python objects
- `Digits` - large digit display
- `Markdown`, `MarkdownViewer` - markdown rendering
- `Rule` - horizontal/vertical line

### Data
- `DataTable` - tabular data with sorting/selection
- `ListView` - scrollable list
- `OptionList` - list with options
- `Tree` - hierarchical tree view
- `DirectoryTree` - file system tree

### Containers
- `Header`, `Footer` - app header/footer
- `Tabs`, `TabbedContent` - tabbed interface
- `Collapsible` - expandable section
- `ContentSwitcher` - switch between child widgets
- `Vertical`, `Horizontal`, `Grid` - layout containers
- `Center` - center contents
- `Container` - general container

### Feedback
- `ProgressBar` - progress indicator
- `LoadingIndicator` - loading spinner
- `Placeholder` - placeholder content
- `Log`, `RichLog` - logging display

---

## Quick Tips

1. **Always await async operations**: `mount()`, `remove()`, `push_screen()`, etc.
2. **Use `await pilot.pause()` in tests** before assertions
3. **Don't modify reactives in `__init__`** - use `set_reactive()` or wait until `on_mount()`
4. **Use semantic color variables** (`$primary`, `$error`) instead of hardcoded colors
5. **Prefer composition over inheritance** for building complex widgets
6. **Keep business logic separate** from UI code
7. **Use workers for async operations** to avoid blocking the UI
8. **Type hint everything** for better IDE support and fewer bugs
9. **Use external CSS files** for easier development with live reload
10. **Test with different terminal sizes** to ensure responsive design

---

For more detailed information, see the [Textual Guide](./guide.md) or visit the [official documentation](https://textual.textualize.io).
