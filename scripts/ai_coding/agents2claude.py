"""Rename all AGENTS.md files to CLAUDE.md under a given workspace."""

import argparse
import os
from pathlib import Path


def agents_to_claude(workspace: str) -> list[Path]:
    renamed = []
    for dirpath, _, filenames in os.walk(workspace):
        if "AGENTS.md" in filenames:
            old_path = Path(dirpath) / "AGENTS.md"
            new_path = Path(dirpath) / "CLAUDE.md"
            old_path.rename(new_path)
            renamed.append(new_path)
    return renamed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rename all AGENTS.md files to CLAUDE.md under a workspace."
    )
    parser.add_argument(
        "workspace",
        nargs="?",
        default="./",
        help="Root directory to search (default: current directory)",
    )
    args = parser.parse_args()

    renamed = agents_to_claude(args.workspace)
    if renamed:
        for path in renamed:
            print(f"Renamed: {path}")
        print(f"\nTotal: {len(renamed)} file(s) renamed.")
    else:
        print("No AGENTS.md files found.")


if __name__ == "__main__":
    main()
