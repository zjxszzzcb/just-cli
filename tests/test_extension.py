#!/usr/bin/env python3
"""
Extension System Tests - Based on README.md Syntax Patterns
============================================================

Tests the 6 core syntax patterns:
1. Command Alias (no parameters)
2. Positional Argument with annotation
3. Option with placeholder replacement
4. Option with multiple arguments
5. Varargs
6. Option Alias
"""

import shlex
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from just.core.config import get_extension_dir
from just.core.extension.generator import generate_extension_script
from just.core.extension.utils import split_command_line


def cleanup(name: str):
    """Cleanup extension files."""
    ext_dir = get_extension_dir()
    
    # Clean script file
    script = ext_dir / f"{name}.py"
    if script.exists():
        script.unlink()
    
    # Clean nested directory
    nested = ext_dir / name
    if nested.exists():
        shutil.rmtree(nested)


def test_pattern(name: str, original_cmd: list, extension_syntax: str, description: str):
    """
    Test a syntax pattern by generating an extension and verifying it compiles.
    
    Args:
        name: Extension name
        original_cmd: Original command parts (e.g., ['echo', 'MESSAGE'])
        extension_syntax: Extension syntax string (e.g., 'just test MESSAGE[msg]')
        description: Test description
    """
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"  Original: {' '.join(original_cmd)}")
    print(f"  Syntax:   {extension_syntax}")
    
    cleanup(name)
    
    # Generate extension
    parts = split_command_line(extension_syntax)
    script_path, _ = generate_extension_script(shlex.join(original_cmd), parts)
    
    # Verify script exists
    assert script_path.exists(), f"Script not found: {script_path}"
    print(f"  Script:   {script_path}")
    
    # Verify script compiles (no syntax errors)
    content = script_path.read_text()
    try:
        compile(content, str(script_path), 'exec')
        print(f"  Compile:  ✅ OK")
    except SyntaxError as e:
        print(f"  Compile:  ❌ FAILED")
        print(f"  Error:    {e}")
        print(f"\n  Generated code:")
        for i, line in enumerate(content.split('\n'), 1):
            print(f"    {i:2}: {line}")
        raise
    
    # Show generated code for inspection
    print(f"  Generated code:")
    for i, line in enumerate(content.split('\n'), 1):
        print(f"    {i:2}: {line}")
    
    cleanup(name)
    print(f"  Result:   ✅ PASSED\n")


def main():
    print("\n" + "="*60)
    print("  EXTENSION SYSTEM TESTS")
    print("  Based on README.md Syntax Patterns")
    print("="*60)
    
    # Pattern 1: Command Alias (no parameters)
    # > just ext add echo "Hello World"
    # >> just echo
    test_pattern(
        name="test1",
        original_cmd=['echo', '"Hello World"'],
        extension_syntax='just test1',
        description='Pattern 1: Command Alias'
    )
    
    # Pattern 2: Positional Argument with full annotation
    # > just ext add echo MESSAGE
    # >> just echo MESSAGE[msg:str="Hello World"#Message to display]
    test_pattern(
        name="test2",
        original_cmd=['echo', 'MESSAGE'],
        extension_syntax='just test2 MESSAGE[msg:str="Hello World"#Message to display]',
        description='Pattern 2: Positional Argument with annotation'
    )
    
    # Pattern 3: Option with placeholder and multiple arguments
    # > just ext add echo MESSAGE TEXT
    # >> just echo -m/--messages MESSAGE[msg] TEXT[text=Messages: ]
    test_pattern(
        name="test3",
        original_cmd=['echo', 'MESSAGE', 'TEXT'],
        extension_syntax='just test3 -m/--messages MESSAGE[msg] TEXT[text=Messages:]',
        description='Pattern 3: Option with multiple arguments'
    )
    
    # Pattern 4: Option with placeholder (single argument)
    # > just ext add echo MESSAGE
    # >> just echo -m/--messages MESSAGE[msg:str="Hello World"#Message to display]
    test_pattern(
        name="test4",
        original_cmd=['echo', 'MESSAGE'],
        extension_syntax='just test4 -m/--messages MESSAGE[msg:str="Hello World"#Message to display]',
        description='Pattern 4: Option with placeholder replacement'
    )
    
    # Pattern 5: Varargs
    # > just ext add echo ARGS
    # >> just echo ARGS[...#Message to display]
    test_pattern(
        name="test5",
        original_cmd=['echo', 'ARGS'],
        extension_syntax='just test5 ARGS[...#Message to display]',
        description='Pattern 5: Varargs'
    )
    
    # Pattern 6: Option Alias
    # > just ext add echo --text
    # >> just echo --text[-m/--messages:str="Hello World"#Text too display]
    test_pattern(
        name="test6",
        original_cmd=['echo', '--text'],
        extension_syntax='just test6 --text[-m/--messages:str="Hello World"#Text to display]',
        description='Pattern 6: Option Alias'
    )
    
    print("\n" + "="*60)
    print("  ALL 6 PATTERNS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
