from just.utils.ext_utils import create_typer_script


create_typer_script(
    custom_command="docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef",
    just_commands=["just", "docker", "ip", "f523e75ca4ef[container_id:str]"],
)