from just import create_typer_app, just_cli

repo_cli = create_typer_app(name="repo", help="Manage plugin repositories.")
just_cli.add_typer(repo_cli)

__all__ = ["repo_cli"]


def _load_commands():
    from .add import add_repo_cmd
    from .remove import remove_repo_cmd
    from .list import list_repo_cmd
    from .update import update_repo_cmd

    repo_cli.command(name="add")(add_repo_cmd)
    repo_cli.command(name="remove")(remove_repo_cmd)
    repo_cli.command(name="list")(list_repo_cmd)
    repo_cli.command(name="update", context_settings={"ignore_unknown_options": True})(update_repo_cmd)


_load_commands()
