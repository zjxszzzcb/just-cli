#!/usr/bin/env python3
"""
Test script for the extension generator functionality.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import just modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from just.core.extension.generator import (
    validate_command_input,
    generate_function_signature,
    generate_command_replacements,
    assemble_typer_script_content
)
from just.core.extension.parser import parse_command_structure
from just.core.extension.utils import split_command_line


def test_split_command_line():
    """Test the split_command_line function with various inputs."""
    print("Testing split_command_line function...\n")

    test_cases = [
        # Basic case without annotations
        {
            'input': 'just simple command arg1 arg2',
            'expected': [
                'just',
                'simple',
                'command',
                'arg1',
                'arg2'
            ],
            'description': 'Basic command without annotations'
        },

        # Case with string annotation containing spaces
        {
            'input': 'just docker ipv4 --container f523e75ca4ef[container_id:str#docker container id or name]',
            'expected': [
                'just',
                'docker',
                'ipv4',
                '--container',
                'f523e75ca4ef[container_id:str#docker container id or name]'
            ],
            'description': 'String annotation with spaces in help message'
        },

        # Case with default value and spaces
        {
            'input': 'just dnslog new --domain log.dnslog.myfw.us[domain:str=log.dnslog.myfw.us#subdomain for DNS logging]',
            'expected': [
                'just',
                'dnslog',
                'new',
                '--domain',
                'log.dnslog.myfw.us[domain:str=log.dnslog.myfw.us#subdomain for DNS logging]'
            ],
            'description': 'Annotation with default value and spaces in help message'
        },

        # Case with boolean flag
        {
            'input': 'just util process --verbose -v[verbose:bool#Enable verbose output]',
            'expected': [
                'just',
                'util',
                'process',
                '--verbose',
                '-v[verbose:bool#Enable verbose output]'
            ],
            'description': 'Boolean flag with help message'
        },

        # Case with numeric type and default
        {
            'input': 'just compress file.txt --level 5[compression_level:int=6#Compression level 1-9]',
            'expected': [
                'just',
                'compress',
                'file.txt',
                '--level',
                '5[compression_level:int=6#Compression level 1-9]'
            ],
            'description': 'Numeric annotation with default and spaces in help'
        },

        # Edge case: empty brackets
        {
            'input': 'just test cmd param[param:str#]',
            'expected': ['just', 'test', 'cmd', 'param[param:str#]'],
            'description': 'Empty help message'
        },

        # Edge case: no help message
        {
            'input': 'just test cmd param[param:str]',
            'expected': ['just', 'test', 'cmd', 'param[param:str]'],
            'description': 'Parameter without help message'
        },

        # Realistic case: help message with parentheses (more common than brackets)
        {
            'input': 'just test cmd param[param:str#help with (parentheses) and spaces]',
            'expected': [
                'just',
                'test',
                'cmd',
                'param[param:str#help with (parentheses) and spaces]'
            ],
            'description': 'Help message containing parentheses'
        },

        # Realistic case: complex help message
        {
            'input': 'just deploy app --config config.json[config_file:str#Path to config file (default: ./config.json)]',
            'expected': [
                'just',
                'deploy',
                'app',
                '--config',
                'config.json[config_file:str#Path to config file (default: ./config.json)]'
            ],
            'description': 'Complex help message with parentheses'
        }
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        input_cmd = test_case['input']
        expected = test_case['expected']
        description = test_case['description']

        try:
            result = split_command_line(input_cmd)

            if result == expected:
                print(f"✅ Test {i}: PASSED - {description}")
                passed += 1
            else:
                print(f"❌ Test {i}: FAILED - {description}")
                print(f"   Input:    {input_cmd}")
                print(f"   Expected: {expected}")
                print(f"   Got:      {result}")
                failed += 1

        except Exception as e:
            print(f"💥 Test {i}: ERROR - {description}")
            print(f"   Input: {input_cmd}")
            print(f"   Error: {e}")
            failed += 1

        print()

    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        print(f"\n❌ {failed} test(s) failed!")
        return False
    else:
        print(f"\n🎉 All {passed} tests passed!")
        return True


def test_validate_command_input():
    """Test the validate_command_input function."""
    print("Testing validate_command_input...")

    # Test with empty list - should raise ValueError
    try:
        validate_command_input([])
        print("❌ Failed: Empty list should raise ValueError")
        return False
    except ValueError:
        print("✅ Passed: Empty list correctly raises ValueError")

    # Test with valid input - should not raise exception
    try:
        validate_command_input(['just', 'test', 'command'])
        print("✅ Passed: Valid input does not raise exception")
        return True
    except Exception as e:
        print(f"❌ Failed: Valid input raised exception: {e}")
        return False


def test_parse_command_structure():
    """Test the parse_command_structure function."""
    print("\nTesting parse_command_structure...")

    # Test basic command without annotations
    commands, arguments, options = parse_command_structure(['just', 'simple', 'command'])
    assert commands == ['just', 'simple', 'command']
    assert len(arguments) == 0
    assert len(options) == 0
    print("✅ Passed: Basic command without annotations")

    # Test command with argument
    commands, arguments, options = parse_command_structure([
        'just', 'docker', 'ip', 'f523e75ca4ef[container_id:str#Container ID]'
    ])
    assert commands == ['just', 'docker', 'ip']
    assert len(arguments) == 1
    assert arguments[0].name == 'container_id'
    assert arguments[0].type.__name__ == 'str'
    assert arguments[0].help == 'Container ID'
    assert len(options) == 0
    print("✅ Passed: Command with argument")

    # Test command with option
    commands, arguments, options = parse_command_structure([
        'just', 'util', 'process', '--verbose', '-v[verbose:bool#Enable verbose output]'
    ])
    assert 'just' in commands
    assert 'util' in commands
    assert 'process' in commands
    assert len(arguments) == 0
    assert len(options) >= 1
    # Find the correct option
    found_option = False
    for key, opt in options.items():
        if opt.name == 'verbose' and opt.type.__name__ == 'bool':
            found_option = True
            break
    assert found_option
    print("✅ Passed: Command with option")

    return True


def test_generate_function_signature():
    """Test the generate_function_signature function."""
    print("\nTesting generate_function_signature...")

    from just.core.extension.parser import Argument

    # Test with no arguments or options
    result = generate_function_signature([], {})
    assert result == '\n'
    print("✅ Passed: No arguments or options")

    # Test with one argument
    args = [Argument('id', 'identifier', str, None, 'ID of the item')]
    result = generate_function_signature(args, {})
    assert 'identifier: Annotated[str, typer.Argument(' in result
    assert 'help=\'ID of the item\'' in result
    print("✅ Passed: One argument")

    # Test with one option
    opts = {
        'v': Argument('v', 'verbose', bool, None, 'Enable verbose output')
    }
    result = generate_function_signature([], opts)
    assert 'verbose: Annotated[bool, typer.Option(' in result
    assert 'help=\'Enable verbose output\'' in result
    print("✅ Passed: One option")

    return True


def test_generate_command_replacements():
    """Test the generate_command_replacements function."""
    print("\nTesting generate_command_replacements...")

    from just.core.extension.parser import Argument

    # Test with no arguments or options
    result = generate_command_replacements([], {})
    assert result == ""
    print("✅ Passed: No arguments or options")

    # Test with one argument
    args = [Argument('f523e75ca4ef', 'container_id', str, None, 'Container ID')]
    result = generate_command_replacements(args, {})
    assert "command = command.replace('f523e75ca4ef', str(container_id))" in result
    print("✅ Passed: One argument")

    # Test with one boolean option
    opts = {
        'v': Argument('v', 'verbose', bool, None, 'Enable verbose output')
    }
    result = generate_command_replacements([], opts)
    assert "if verbose:" in result
    assert "command = command.replace('v', 'v')" in result
    print("✅ Passed: One boolean option")

    return True


def test_assemble_typer_script_content():
    """Test the assemble_typer_script_content function."""
    print("\nTesting assemble_typer_script_content...")

    custom_command = "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef"
    parent_cmd = "docker"
    sub_cmd = "ip"
    signature = "    container_id: Annotated[str, typer.Argument(\n        help='Container ID',\n        show_default=False\n    )]\n"
    replacements = "    command = command.replace('f523e75ca4ef', str(container_id))"

    result = assemble_typer_script_content(custom_command, parent_cmd, sub_cmd, signature, replacements)

    # Check that key elements are present
    assert 'import shlex' in result
    assert 'import subprocess' in result
    assert 'import typer' in result
    assert f'{sub_cmd}_cli = create_typer_app()' in result
    assert f'@{sub_cmd}_cli.command(name="{sub_cmd}")' in result
    assert custom_command in result
    print("✅ Passed: Script content assembled correctly")

    return True


def run_all_tests():
    """Run all tests."""
    print("Running extension generator tests...\n")

    tests = [
        test_split_command_line,
        test_validate_command_input,
        test_parse_command_structure,
        test_generate_function_signature,
        test_generate_command_replacements,
        test_assemble_typer_script_content
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)