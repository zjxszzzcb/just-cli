#!/usr/bin/env python3
"""
Extension System Tests - Fail Fast
===================================
Tests crash immediately on error for easy debugging.
"""

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from just.core.config import get_extension_dir
from just.core.extension.generator import generate_extension_script
from just.core.extension.utils import split_command_line


def cleanup(name: str):
    """Cleanup extension."""
    ext_dir = get_extension_dir()
    script = ext_dir / f"{name}.py"
    if script.exists():
        script.unlink()
    nested = ext_dir / name
    if nested.exists():
        shutil.rmtree(nested)
    pycache = ext_dir / '__pycache__'
    if pycache.exists():
        shutil.rmtree(pycache)


def run_just(args):
    """Run just command and return stdout."""
    result = subprocess.run(['just'] + args, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
    return result.stdout


def test(name, original, syntax, help_contains=None, exec_args=None, exec_contains=None):
    """Test an extension."""
    print(f"\n=== {name} ===")
    cleanup(name)
    
    # Generate
    print(f"  Generating: {syntax}")
    parts = split_command_line(syntax)
    generate_extension_script(shlex.join(original), parts)
    
    # Show script
    ext_dir = get_extension_dir()
    script = ext_dir / f"{name}.py"
    if not script.exists():
        # Try nested
        script = ext_dir / parts[1] / f"{parts[2].split('[')[0]}.py"
    
    assert script.exists(), f"Script not found: {script}"
    print(f"  Script: {script}")
    content = script.read_text()
    for i, line in enumerate(content.split('\n'), 1):
        print(f"    {i:2}: {line}")
    
    # Test help
    print(f"  Testing: just {name} -h")
    stdout = run_just([name, '-h'])
    print(f"  Help output (first 500 chars):")
    print(f"    {stdout[:500]}")
    
    if help_contains:
        for expected in help_contains:
            assert expected.lower() in stdout.lower(), f"Help missing: {expected}"
            print(f"  ✅ Help contains: {expected}")
    
    # Test execution
    if exec_args is not None:
        print(f"  Testing: just {name} {' '.join(exec_args)}")
        stdout = run_just([name] + exec_args)
        print(f"  Output: {stdout.strip()}")
        
        if exec_contains:
            assert exec_contains in stdout, f"Output missing: {exec_contains}"
            print(f"  ✅ Output contains: {exec_contains}")
    
    cleanup(name)
    print(f"  ✅ PASSED")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  EXTENSION SYSTEM TESTS (Fail Fast)")
    print("="*60)
    
    # Basic positional argument
    test(
        name="testarg1",
        original=['echo', 'MESSAGE'],
        syntax='just testarg1 MESSAGE[message]',
        help_contains=['message'],
        exec_args=['Hello'],
        exec_contains='Hello'
    )
    
    # Typed argument
    test(
        name="testarg2",
        original=['echo', 'MESSAGE'],
        syntax='just testarg2 MESSAGE[message:str]',
        help_contains=['message'],
        exec_args=['World'],
        exec_contains='World'
    )
    
    # Argument with default
    test(
        name="testarg3",
        original=['echo', 'MESSAGE'],
        syntax='just testarg3 MESSAGE[message:str=DefaultValue]',
        help_contains=['message'],
        exec_args=[],
        exec_contains='DefaultValue'
    )
    
    # Option
    test(
        name="testopt1",
        original=['echo', 'VALUE'],
        syntax='just testopt1 --msg VALUE[message:str]',
        help_contains=['--msg'],
        exec_args=['--msg', 'OptionTest'],
        exec_contains='OptionTest'
    )
    
    # Alias
    test(
        name="testalias1",
        original=['echo', 'VALUE'],
        syntax='just testalias1 -m/--message VALUE[msg:str]',
        help_contains=['-m', '--message'],
        exec_args=['-m', 'Short'],
        exec_contains='Short'
    )
    
    print("\n" + "="*60)
    print("  ALL TESTS PASSED!")
    print("="*60 + "\n")
