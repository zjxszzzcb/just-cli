"""Rename all CLAUDE.md files to AGENTS.md under a given workspace."""

import argparse
import os
from pathlib import Path


def claude_to_agents(workspace: str) -> list[Path]:
    renamed = []
    for dirpath, _, filenames in os.walk(workspace):
        if "CLAUDE.md" in filenames:
            old_path = Path(dirpath) / "CLAUDE.md"
            new_path = Path(dirpath) / "AGENTS.md"
            old_path.rename(new_path)
            renamed.append(new_path)
    return renamed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rename all CLAUDE.md files to AGENTS.md under a workspace."
    )
    parser.add_argument(
        "workspace",
        nargs="?",
        default="./",
        help="Root directory to search (default: current directory)",
    )
    args = parser.parse_args()

    renamed = claude_to_agents(args.workspace)
    if renamed:
        for path in renamed:
            print(f"Renamed: {path}")
        print(f"\nTotal: {len(renamed)} file(s) renamed.")
    else:
        print("No CLAUDE.md files found.")


if __name__ == "__main__":
    main()
