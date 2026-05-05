from just import echo
from just.core.repo import list_repos

from rich.console import Console
from rich.table import Table


def list_repo_cmd() -> None:
    """List all installed plugin repositories."""
    repos = list_repos()

    if not repos:
        echo.info("No repos installed. Use 'just repo add <name> <url>' to add one.")
        return

    console = Console()
    table = Table(
        title="Plugin Repositories",
        title_style="bold cyan",
        header_style="bold green",
        border_style="dim",
    )

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("URL", style="white", no_wrap=False)
    table.add_column("Branch", style="yellow")
    table.add_column("Commit", style="dim")
    table.add_column("Commands", style="green")
    table.add_column("Installers", style="green")

    for repo in repos:
        table.add_row(
            repo["name"],
            repo["url"],
            repo["branch"],
            repo["commit"],
            "Yes" if repo["has_commands"] else "-",
            "Yes" if repo["has_installers"] else "-",
        )

    console.print()
    console.print(table)
    console.print()
