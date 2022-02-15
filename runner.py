import click
from rich.traceback import install

from declutter import __version__
from declutter.cli import commands

install(suppress=[click])

declutter_commands = {
    "what": commands.declutter_what_command,
    "organise": commands.declutter_organise_command,
    "watch": commands.declutter_watch_command,
    "oldies": commands.declutter_oldies_command,
}


@click.group(commands=declutter_commands)
@click.version_option(__version__)
def __declutter_cli__():
    pass


if __name__ == "__main__":
    __declutter_cli__()
