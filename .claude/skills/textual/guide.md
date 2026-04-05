# Comprehensive Textual Framework Guide

A complete guide to building TUI (Text User Interface) applications with Textual.

## Table of Contents

1. [Core Concepts & Architecture](#core-concepts--architecture)
2. [Directory Structure & Code Organization](#directory-structure--code-organization)
3. [Testing](#testing)
4. [Design & Best Practices](#design--best-practices)
5. [Common Errors & Pitfalls](#common-errors--pitfalls)
6. [Architectural Patterns](#architectural-patterns)

---

## Core Concepts & Architecture

### How Textual Applications Work

**Event-Driven Architecture:**
- When you call `app.run()`, Textual enters "application mode," taking control of the terminal
- Uses an **asynchronous message queue system** where events are processed sequentially
- Each App and Widget has its own message queue for handling events
- Messages are dispatched to handler methods asynchronously
- The system guarantees message handling even when handlers aren't immediately available

**The DOM (Document Object Model):**
- Textual implements a DOM-like structure where widgets form a tree hierarchy
- Widgets can contain child widgets, similar to web browsers
- Query and manipulate widgets using CSS selectors:
  - `query_one()` - retrieves a single widget
  - `query()` - returns a DOMQuery object (list-like) of matching widgets
  - Supports refinement: `first()`, `last()`, `filter()`, `exclude()`

**Event Bubbling:**
- Events bubble up the DOM hierarchy by default
- Input events propagate from child widgets to parents
- Call `event.stop()` to halt propagation when a widget has handled an event

### Key Components

#### App Class

The foundation class serving as the entry point for all Textual applications.

**Key Attributes:**
- `CSS_PATH` - reference external .tcss files
- `CSS` - inline styles
- `TITLE` / `SUB_TITLE` - header information
- `SCREENS` - map screen names to screen classes
- `BINDINGS` - keyboard shortcuts
- `MODES` - independent screen stacks for different contexts

**Basic Example:**
```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static

class MyApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "My Application"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Welcome to my app!")
        yield Button("Click me", id="main-button")
        yield Footer()

    def on_mount(self) -> None:
        """Called after entering application mode."""
        # Initialize application state
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        self.query_one(Static).update("Button was clicked!")

if __name__ == "__main__":
    app = MyApp()
    app.run()  # Returns exit value
```

#### Screens

Containers for widgets that occupy the entire terminal dimensions.

**Key Points:**
- Only one screen is active at any time
- Textual auto-creates a default screen if you don't specify one
- Screens function like mini-apps: support key bindings, compose methods, and CSS
- Can be pushed, popped, and switched dynamically

**Screen Stack Management:**
```python
# Push screen onto stack (becomes active)
self.push_screen("settings")

# Pop topmost screen (at least one must remain)
self.pop_screen()

# Replace top screen with new one
self.switch_screen("help")

# Pop screen and pass data to callback
self.dismiss(result_data)
```

**Modal Screens:**
```python
from textual.screen import ModalScreen

class ConfirmDialog(ModalScreen[bool]):
    """Type-safe modal that returns a boolean."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Are you sure?")
            with Horizontal():
                yield Button("Yes", id="yes")
                yield Button("No", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

# Usage in app
def action_delete(self) -> None:
    def handle_result(confirmed: bool) -> None:
        if confirmed:
            self.delete_item()

    self.push_screen(ConfirmDialog(), handle_result)
```

#### Widgets

Reusable UI components managing rectangular screen regions.

**Creating Custom Widgets:**
```python
from textual.widget import Widget

class Hello(Widget):
    def render(self) -> str:
        return "Hello, [b]World[/b]!"  # Supports Rich markup
```

**The Static Widget:**
- Caches render results for performance
- Provides `update()` method for refreshing content without full redraws
- Best for simple text display widgets

**Widget Features:**
```python
class CustomWidget(Widget):
    DEFAULT_CSS = """
    CustomWidget {
        border: solid blue;
        padding: 1;
    }
    """

    can_focus = True  # Make widget focusable

    BINDINGS = [
        ("enter", "select", "Select item"),
        ("space", "toggle", "Toggle"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.border_title = "My Widget"
        self.tooltip = "This is a helpful tooltip"
```

### CSS Styling System (TCSS)

**Philosophy:** CSS separates how your app looks from how it works.

**Key Features:**
- External `.tcss` files via `CSS_PATH` or inline with `CSS` class variable
- Supports live editing with `textual run --dev my_app.py`
- Changes reflect in terminal within milliseconds

**Selectors:**
```css
/* Type selector */
Button {
    background: green;
}

/* ID selector */
#next {
    outline: red;
}

/* Class selector */
.success {
    background: green;
}

/* Universal selector */
* {
    border: solid white;
}

/* Pseudo classes */
Button:hover {
    background: blue;
}

Button:focus {
    border: solid yellow;
}

.form-input:disabled {
    opacity: 0.5;
}
```

**Combinators:**
```css
/* Descendant - any nested descendant */
#dialog Button {
    margin: 1;
}

/* Child - only direct children */
#sidebar > Button {
    width: 100%;
}
```

**Advanced Features:**
```css
/* CSS Variables */
Screen {
    background: $surface;
}

Button {
    background: $primary;
}

/* Nesting with & selector */
Button {
    background: $primary;

    &:hover {
        background: $primary-lighten-1;
    }

    &.danger {
        background: $error;
    }
}

/* !important for override (use sparingly) */
.critical {
    background: red !important;
}

/* initial to reset to defaults */
Button {
    border: initial;
}
```

### Reactive System & Data Binding

Reactive attributes are class-level attributes that automatically trigger UI updates when changed.

**Basic Usage:**
```python
from textual.reactive import reactive
from textual.widget import Widget

class Counter(Widget):
    count = reactive(0)  # Reactive attribute

    def render(self) -> str:
        return f"Count: {self.count}"

    def on_button_pressed(self) -> None:
        self.count += 1  # Automatically triggers render()
```

**Key Features:**

**1. Smart Refresh:**
- Multiple changes trigger only one refresh for efficiency
- Automatic calls to `render()` when reactive values change

**2. Validation:**
```python
class Counter(Widget):
    count = reactive(0)

    def validate_count(self, value: int) -> int:
        """Constrain values before assignment."""
        return max(0, min(value, 100))
```

**3. Watch Methods:**
```python
class Counter(Widget):
    count = reactive(0)

    def watch_count(self, old_value: int, new_value: int) -> None:
        """React to changes."""
        if new_value > 10:
            self.add_class("high")
        else:
            self.remove_class("high")
```

**4. Computed Properties:**
```python
class Calculator(Widget):
    count = reactive(0)
    doubled = reactive(0)

    def compute_doubled(self) -> int:
        """Auto-recalculates when count changes."""
        return self.count * 2
```

**5. Recompose:**
```python
class ViewSwitcher(Widget):
    mode = reactive("list", recompose=True)

    def compose(self) -> ComposeResult:
        if self.mode == "list":
            yield ListView()
        else:
            yield GridView()

    def toggle_mode(self) -> None:
        self.mode = "grid" if self.mode == "list" else "list"
        # Widget automatically recomposes
```

**6. Data Binding:**
```python
class ParentWidget(Widget):
    value = reactive(0)

    def compose(self) -> ComposeResult:
        child = ChildWidget()
        # Bind child's display_value to parent's value
        child.data_bind(self, display_value="value")
        yield child

class ChildWidget(Widget):
    display_value = reactive(0)

    def render(self) -> str:
        return f"Value: {self.display_value}"
```

---

## Directory Structure & Code Organization

### Recommended Project Structures

#### Option 1: Separated Screens and Widgets

Best for medium to large applications with clear separation of concerns.

```
project_name/
├── src/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── app.py               # Main App class
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── main_screen.py
│   │   ├── settings_screen.py
│   │   └── help_screen.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── status_bar.py
│   │   ├── data_grid.py
│   │   └── custom_input.py
│   └── business_logic/
│       ├── __init__.py
│       ├── models.py        # Data models
│       ├── services.py      # API calls, business logic
│       └── validators.py    # Validation functions
├── static/                  # Optional: external CSS
│   ├── app.tcss
│   ├── screens/
│   │   └── main_screen.tcss
│   └── widgets/
│       └── status_bar.tcss
├── tests/
│   ├── test_app.py
│   ├── test_screens/
│   └── test_widgets/
├── pyproject.toml
└── README.md
```

### Organization Best Practices

#### 1. Widget Communication Pattern

**"Attributes down, messages up"** - Textual's recommended data flow pattern.

- A widget can update a child by setting its attributes or calling methods
- Widgets should only send messages to their parent
- This creates uni-directional data flow

```python
# Parent widget
class ParentWidget(Widget):
    def compose(self) -> ComposeResult:
        yield ChildWidget(initial_value=10)

    def on_child_updated(self, message: ChildWidget.Updated) -> None:
        """Handle message from child."""
        self.log(f"Child updated: {message.new_value}")

# Child widget
class ChildWidget(Widget):
    class Updated(Message):
        """Posted when child value changes."""
        def __init__(self, new_value: int) -> None:
            super().__init__()
            self.new_value = new_value

    def __init__(self, initial_value: int = 0) -> None:
        super().__init__()
        self.value = initial_value

    def increment(self) -> None:
        self.value += 1
        self.post_message(self.Updated(self.value))
```

#### 2. CSS Organization

**For Widgets:**
- Use `DEFAULT_CSS` class variable to bundle styling with distributable widgets
- CSS_PATH only available for App and Screen classes

```python
class StatusBar(Widget):
    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text-muted;
    }
    """
```

**For Apps:**
- Keep CSS in external files for live editing during development
- Organize by screens and major components

#### 3. Compound Widgets

Build complex widgets from simpler ones through composition.

**Rule of thumb:** A widget should handle one piece of data or one logical UI component.

```python
# Simple widgets
class StatusIcon(Widget):
    def render(self) -> str:
        return "✓"

class StatusText(Static):
    pass

class StatusButton(Button):
    pass

# Compound widget
class StatusPanel(Widget):
    """Combines multiple simple widgets."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield StatusIcon()
            yield StatusText("Ready")
            yield StatusButton("Refresh")
```

---

## Testing

### Testing Framework Setup

**Recommended Stack:**
- **pytest** - testing framework
- **pytest-asyncio** - async test support
- **pytest-textual-snapshot** - visual regression testing (optional)

**Installation:**
```bash
pip install pytest pytest-asyncio pytest-textual-snapshot
```

**pytest.ini configuration:**
```ini
[pytest]
asyncio_mode = auto
```

### Core Testing Pattern

**The `run_test()` Context Manager:**
- Runs app in "headless" mode (no terminal rendering)
- Returns `Pilot` object for simulating user interactions
- Maintains normal app behavior for assertions

**Basic Test Example:**
```python
import pytest
from my_app import MyApp

@pytest.mark.asyncio
async def test_button_click():
    app = MyApp()
    async with app.run_test() as pilot:
        # Simulate user pressing button
        await pilot.click("#submit-button")

        # Wait for async processing
        await pilot.pause()

        # Assertions
        result = app.query_one("#result", Static)
        assert result.renderable == "Success"
```

### Pilot Methods for Simulation

**Keyboard Input:**
```python
# Single key press
await pilot.press("enter")

# Multiple keys
await pilot.press("h", "e", "l", "l", "o")

# Modifiers
await pilot.press("ctrl+c")
await pilot.press("shift+tab")

# Named keys
await pilot.press("tab", "down", "up", "escape", "pagedown")
```

**Mouse Interaction:**
```python
# Click by selector
await pilot.click("#my-button")

# Click by widget type
await pilot.click(Button)

# Click by coordinates
await pilot.click(offset=(10, 5))

# Double/triple click
await pilot.click("#item", times=2)

# Click with modifiers
await pilot.click("#file", shift=True)
await pilot.click("#item", ctrl=True)
```

**Async Handling:**
```python
# Wait for pending messages to process
await pilot.pause()

# Essential before assertions to ensure UI has updated
# This is the most common mistake in testing!
```

### Testing Best Practices

**1. Always Use `await pilot.pause()`:**
```python
# WRONG - race condition
await pilot.click("#button")
assert app.query_one("#status").text == "Done"  # May fail!

# RIGHT
await pilot.click("#button")
await pilot.pause()  # Wait for message processing
assert app.query_one("#status").text == "Done"
```

**2. Query Widgets for Assertions:**
```python
# Get specific widget by ID
result = app.query_one("#result", Static)
assert result.renderable == "Expected text"

# Get by type
button = app.query_one(Button)
assert button.label == "Click me"

# Check multiple widgets
buttons = app.query("Button.enabled")
assert len(buttons) == 3

# Check widget state
assert widget.has_class("active")
assert widget.disabled is False
```

---

## Design & Best Practices

### UI/UX Best Practices for TUI Apps

#### 1. Start with a Visual Sketch

- Use pen and paper to draw rectangles representing UI elements
- Annotate with content and behavior (scrolling, fixed positioning, etc.)
- Prevents costly redesigns later
- Helps identify layout patterns early

#### 2. Work Outside-In

> "Like sculpting with a block of marble, work from outside towards center"

- Implement fixed elements first (headers, footers, sidebars)
- Then add flexible content areas
- This creates a stable layout foundation

**Example:**
```python
def compose(self) -> ComposeResult:
    # 1. Fixed elements first
    yield Header()

    # 2. Container for main layout
    with Horizontal():
        # 3. Fixed sidebar
        yield Sidebar()

        # 4. Flexible content area (fills remaining space)
        yield ContentArea()

    # 5. Fixed footer
    yield Footer()
```

#### 3. Docking for Fixed Elements

```css
#header {
    dock: top;
    height: 3;
}

#footer {
    dock: bottom;
    height: 1;
}

#sidebar {
    dock: left;
    width: 30;
}
```

#### 4. Use FR Units for Flexible Space

```css
#content {
    width: 1fr;   /* Fill available width */
    height: 1fr;  /* Fill available height */
}

/* Split area into proportional sections */
#left-panel {
    width: 1fr;   /* Takes 1 part */
}

#right-panel {
    width: 2fr;   /* Takes 2 parts (twice as wide) */
}
```

### Theme System & Colors

#### 11 Base Colors Generate Complete Palette

**Semantic Color Roles:**
- `$primary` - primary branding color
- `$secondary` - alternative branding
- `$warning` - warning status
- `$error` - error status
- `$success` - success status
- `$accent` - accent highlights
- `$background` - main background
- `$surface` - raised surface
- `$panel` - panel backgrounds
- `$boost` - attention-grabbing elements
- `$dark` - dark elements

**Auto-generated Shades:**
Each color gets 3 light + 3 dark variants:
- `-darken-1`, `-darken-2`, `-darken-3`
- `-lighten-1`, `-lighten-2`, `-lighten-3`
- `-muted` - desaturated variant for secondary areas

**Text Colors with Legibility Guarantees:**
- `$text` - auto-adjusts to light/dark based on background
- `$text-muted` - secondary information
- `$text-disabled` - non-interactive elements

**Best Practices:**
```css
/* GOOD - semantic colors */
#header {
    background: $primary;
    color: $text;
}

.warning-message {
    background: $warning;
    color: $text;
}

#sidebar {
    background: $surface;
}

/* AVOID - hardcoded colors */
#header {
    background: #3498db;  /* What does this represent? */
}
```

### Performance Considerations

#### 1. Target 60fps

Modern terminals support hardware acceleration - smooth performance is achievable.

#### 2. Use Immutable Objects

```python
from dataclasses import dataclass

# Immutable data structures
@dataclass(frozen=True)
class UserData:
    id: int
    name: str
    email: str

# Easier to reason about, cache, and test
# Reduces side-effects in layout calculations
```

#### 3. Leverage Static Widget

```python
from textual.widgets import Static

# Static caches render results automatically
class StatusDisplay(Static):
    def update_status(self, message: str) -> None:
        # Only updates when content changes
        self.update(message)
```

---

## Common Errors & Pitfalls

### Typical Mistakes Beginners Make

#### 1. Forgetting Async/Await

```python
# WRONG
def on_button_pressed(self):
    self.mount(Widget())  # Missing await

# RIGHT
async def on_button_pressed(self):
    await self.mount(Widget())
```

Many Textual methods are async and must be awaited:
- `mount()`, `unmount()`, `remove()`
- `push_screen()`, `pop_screen()`, `switch_screen()`
- Any method that returns a coroutine

#### 2. Not Waiting for Message Processing in Tests

```python
# WRONG - assertion may run before UI updates
async def test_feature():
    await pilot.click("#button")
    assert app.query_one("#status").text == "Done"  # Race condition!

# RIGHT
async def test_feature():
    await pilot.click("#button")
    await pilot.pause()  # Wait for messages to process
    assert app.query_one("#status").text == "Done"
```

#### 3. Modifying Reactive Attributes in `__init__`

```python
# WRONG - triggers watchers before widget is mounted
def __init__(self):
    super().__init__()
    self.count = 10  # Triggers watch_count before ready!

# RIGHT - Option 1: use set_reactive
def __init__(self):
    super().__init__()
    self.set_reactive(MyWidget.count, 10)  # No watcher invocation

# RIGHT - Option 2: set in on_mount
def __init__(self):
    super().__init__()

def on_mount(self):
    self.count = 10  # Safe to trigger watchers now
```

#### 4. Blocking the Event Loop

```python
# WRONG - blocks UI
def on_button_pressed(self):
    response = requests.get("https://api.example.com")  # Blocking!
    self.display_result(response.json())

# RIGHT - use workers
from textual.worker import work

@work(exclusive=True)
async def on_button_pressed(self):
    # Use async HTTP library
    response = await httpx.get("https://api.example.com")
    self.display_result(response.json())
```

### Debugging Strategies

#### 1. Development Console

**Terminal 1 - Start console:**
```bash
textual console
```

**Terminal 2 - Run app with dev mode:**
```bash
textual run --dev my_app.py
```

**In your code:**
```python
from textual import log

def on_button_pressed(self):
    log("Button pressed!")
    log("Current state:", self.state)
    log(locals())  # Log all local variables
```

#### 2. Visual Debugging with Borders

```css
/* Temporarily add borders to see layout structure */
* {
    border: solid red;
}

/* Or specific widgets */
.debug {
    border: solid yellow;
}
```

---

## Architectural Patterns

### Composition vs Inheritance

#### Prefer Composition

> "Build compound widgets by combining simpler ones"

**Why?**
- More flexible and reusable
- Easier to test individual components
- Follows "has-a" relationships naturally
- Reduces coupling

**Example:**
```python
# GOOD - Composition
class UserCard(Widget):
    """Composed of smaller, focused widgets."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Avatar()           # Simple widget
            yield UserName()         # Simple widget
            yield UserEmail()        # Simple widget
            yield ActionButtons()    # Simple widget

class Avatar(Static):
    """Single-purpose: display avatar."""
    def render(self) -> str:
        return "👤"
```

### State Management Approaches

#### 1. Local Widget State (Simple)

Best for: Widget-specific state that doesn't need to be shared.

```python
class Counter(Widget):
    count = reactive(0)

    def increment(self) -> None:
        self.count += 1

    def render(self) -> str:
        return f"Count: {self.count}"
```

#### 2. App-Level State (Medium)

Best for: Global application state accessible from any widget.

```python
class MyApp(App):
    # App-level reactive state
    user_name = reactive("")
    is_authenticated = reactive(False)

    def login(self, username: str) -> None:
        self.user_name = username
        self.is_authenticated = True

# Any widget can access via self.app
class UserWidget(Widget):
    def render(self) -> str:
        if self.app.is_authenticated:
            return f"Welcome, {self.app.user_name}!"
        return "Please log in"
```

#### 3. Message-Based State (Complex)

Best for: Decoupled communication between widgets, event-driven updates.

```python
class DataUpdated(Message):
    """Posted when data changes."""
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data

class DataWidget(Widget):
    def update_data(self, data: dict) -> None:
        """Update data and notify listeners."""
        self.data = data
        self.post_message(DataUpdated(data))

class ListenerWidget(Widget):
    def on_data_updated(self, message: DataUpdated) -> None:
        """Handle data updates from any source."""
        self.refresh_display(message.data)
```

### How to Keep Code Simple and Maintainable

#### 1. Single Responsibility Principle

Each widget should have one clear purpose.

```python
# BETTER - separate concerns
class UserPanel(Widget):
    """Only handles UI presentation."""

    def __init__(self) -> None:
        super().__init__()
        self.service = UserService()
        self.validator = UserValidator()

    def compose(self) -> ComposeResult:
        # Just UI
        yield UserForm()
        yield UserActions()

# business_logic/services.py
class UserService:
    async def fetch_user(self, user_id: int) -> User:
        # API calls
        pass

# business_logic/validators.py
class UserValidator:
    def validate(self, data: dict) -> bool:
        # Validation logic
        pass
```

#### 2. Use Type Hints

```python
from textual.app import App, ComposeResult
from textual.widgets import Button, Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Button("Click", id="main-button")
        yield Static("Status", id="status")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button: Button = event.button
        button.label = "Clicked"

        status: Static = self.query_one("#status", Static)
        status.update("Button was clicked")
```

---

## Conclusion

This guide covers the essential concepts, patterns, and best practices for building maintainable TUI applications with Textual. Key takeaways:

1. **Architecture**: Event-driven with reactive programming
2. **Organization**: Separate UI from business logic, prefer composition
3. **Testing**: Use pytest with Pilot for simulation
4. **Design**: Sketch first, work outside-in, use semantic colors
5. **Performance**: Cache aggressively, use immutable objects, target 60fps
6. **Maintainability**: Keep widgets focused, use type hints, document complex code

For more information, visit the [official Textual documentation](https://textual.textualize.io).
