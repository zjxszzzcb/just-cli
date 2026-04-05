# Textual Skill

Expert guidance for building TUI (Text User Interface) applications with the Textual framework.

## Overview

This skill provides comprehensive knowledge about building terminal user interfaces with Textual, a modern Python framework by Textualize.io. It covers:

- **Core Concepts**: App architecture, screens, widgets, reactive programming, CSS styling
- **Best Practices**: Design patterns, code organization, performance optimization
- **Testing**: Testing strategies with pytest and Pilot
- **Debugging**: Development console, logging, visual debugging
- **Common Patterns**: Ready-to-use code templates and examples
- **Error Prevention**: Common pitfalls and how to avoid them

## Files

- **SKILL.md**: Main skill definition with invocation triggers and high-level guidance
- **quick-reference.md**: Concise cheat sheets, templates, and quick lookups
- **guide.md**: Comprehensive architectural guide with detailed explanations
- **README.md**: This file - skill documentation

## When This Skill is Invoked

Claude will automatically use this skill when you:

- Ask about building TUI applications
- Mention the Textual framework
- Need help with widgets, screens, or layouts
- Have questions about CSS styling (TCSS)
- Want to implement reactive programming
- Need testing guidance for Textual apps
- Encounter errors with Textual code
- Ask about TUI design patterns

## Usage Examples

**Basic Questions:**
- "How do I create a Textual app?"
- "What's the best way to organize a Textual project?"
- "How do I test Textual applications?"

**Specific Features:**
- "How do I create a modal dialog in Textual?"
- "What's the difference between reactive and var?"
- "How do I make a widget focusable?"

**Debugging:**
- "Why isn't my reactive attribute updating the UI?"
- "My test is failing - what am I doing wrong?"
- "How do I debug a Textual app?"

**Design & Architecture:**
- "What's the best state management approach for my Textual app?"
- "Should I use composition or inheritance for my widgets?"
- "How do I implement the 'attributes down, messages up' pattern?"

## Key Concepts Covered

### Architecture
- Event-driven message queue system
- DOM-like widget hierarchy
- Screen navigation and modes
- Widget lifecycle methods

### Reactive Programming
- Reactive attributes with auto-refresh
- Validation and watch methods
- Computed properties
- Data binding between widgets
- Recompose for dynamic layouts

### CSS Styling (TCSS)
- Selector types and specificity
- Layout with docking and FR units
- Theme system with semantic colors
- Pseudo-classes and nesting
- Live reload during development

### Testing
- pytest with async support
- Pilot for simulating interactions
- Snapshot testing (optional)
- Common testing patterns
- Best practices and pitfalls

### Best Practices
- "Attributes down, messages up" pattern
- Composition over inheritance
- Single responsibility principle
- Separation of UI and business logic
- Performance optimization
- Accessibility considerations

## Quick Start

To build a minimal Textual app:

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

Run with:
```bash
python my_app.py
```

Or use development mode for live reload:
```bash
textual run --dev my_app.py
```

## Resources

- **Official Documentation**: https://textual.textualize.io
- **GitHub**: https://github.com/Textualize/textual
- **Discord**: Join the Textual Discord for community support

## Skill Maintenance

This skill is based on the Textual documentation and best practices as of January 2025. The framework is actively developed, so refer to the official documentation for the latest features and changes.

### Original Source Files

This skill was created from:
- `textual-quick-reference.md` - Quick reference templates
- `textual-guide.md` - Comprehensive framework guide

These files can be updated and the skill regenerated if needed.
