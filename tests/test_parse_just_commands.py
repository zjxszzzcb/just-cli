#!/usr/bin/env python3
"""
Test script for parse_just_commands function to prevent regression.
"""

import sys

from just.commands.extension.add import parse_just_commands


def test_parse_just_commands():
    """Test the parse_just_commands function with various inputs."""

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
            'input': 'just docker ipv4 '
                     '--container f523e75ca4ef[container_id:str#docker container id or name]',
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
            'input': 'just dnslog new '
                     '--domain log.dnslog.myfw.us[domain:str=log.dnslog.myfw.us#subdomain for DNS logging]',
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
            'input': 'just util process '
                     '--verbose -v[verbose:bool#Enable verbose output]',
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
            'input': 'just compress '
                     'file.txt '
                     '--level 5[compression_level:int=6#Compression level 1-9]',
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
            'input': 'just test cmd '
                     'param[param:str#help with (parentheses) and spaces]',
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
            'input': 'just deploy app '
                     '--config config.json[config_file:str#Path to config file (default: ./config.json)]',
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

    print("Testing parse_just_commands function...\n")

    for i, test_case in enumerate(test_cases, 1):
        input_cmd = test_case['input']
        expected = test_case['expected']
        description = test_case['description']

        try:
            result = parse_just_commands(input_cmd)

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


if __name__ == "__main__":
    success = test_parse_just_commands()
    sys.exit(0 if success else 1)