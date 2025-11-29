import unittest
import sys
import shutil
import tempfile
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from just.core.extension.utils import split_command_line
from just.core.extension.parser import parse_command_structure

class TestExtensionSystem(unittest.TestCase):
    """
    Documentation for Extension System
    ==================================
    
    The Extension System allows users to add custom commands.
    This suite demonstrates how commands are parsed and processed.
    """

    def test_command_parsing_simple(self):
        """
        Scenario: Parsing a Simple Command
        
        Input: just mycmd arg1
        Expected: Command parts are correctly identified.
        """
        print("\n   Testing simple command parsing...")
        cmd = "just mycmd arg1"
        parts = split_command_line(cmd)
        self.assertEqual(parts, ['just', 'mycmd', 'arg1'])
        print(f"   Input: '{cmd}' -> Parsed: {parts}")
        print("   ✅ Simple parsing successful")

    def test_command_parsing_with_annotations(self):
        """
        Scenario: Parsing Command with Type Annotations
        
        Input: just docker ip container_id[id:str#Container ID]
        Expected: The annotation is preserved in the last part.
        """
        print("\n   Testing annotated command parsing...")
        cmd = "just docker ip container_id[id:str#Container ID]"
        parts = split_command_line(cmd)
        self.assertEqual(parts[-1], "container_id[id:str#Container ID]")
        print(f"   Input: '{cmd}' -> Parsed: {parts}")
        print("   ✅ Annotated parsing successful")

    def test_structure_analysis(self):
        """
        Scenario: Analyzing Command Structure
        
        This demonstrates how the system understands arguments and options from the parsed command.
        """
        print("\n   Testing structure analysis...")
        parts = ['just', 'docker', 'ip', 'container_id[id:str#Container ID]']
        commands, args, options = parse_command_structure(parts)
        
        print(f"   Commands: {commands}")
        print(f"   Arguments: {[a.name for a in args]}")
        
        self.assertEqual(commands, ['just', 'docker', 'ip'])
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0].name, 'id')
        self.assertEqual(args[0].help, 'Container ID')
        print("   ✅ Structure analysis successful")

if __name__ == '__main__':
    unittest.main()
