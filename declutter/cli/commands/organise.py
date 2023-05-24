"""
Organise directories 
"""

from pathlib import Path
from shutil import move

import click
import rich

from ... import SPECIAL_DIRECTORIES, iter_organisation


def safe_move(console, source: Path, destination: Path):

    try:
        move(source, destination)
    except Exception as e:
        console.print(
            f"[red]Could not move {source} to {destination} due to {e!r}.[/red]".format()
        )


@click.command()
@click.argument("path", required=False, default=".", type=str)
@click.option(
    "-e",
    "--exempt",
    help="Path that are not to be touched during the procedure.",
    required=False,
    multiple=True,
)
@click.option(
    "-r",
    "--recurse",
    help="Recursively organise the directory.",
    required=False,
    is_flag=True,
)
def declutter_organise_command(path, exempt, recurse: bool):
    exempt_path = map(Path, exempt)
    console = rich.get_console()

    for source, destination in (
        (src, dest)
        for src, dest in iter_organisation(Path(path), recurse=recurse)
        if not (dest in (src, src.parent) or any(check == src for check in exempt_path))
    ):
        if source.name in SPECIAL_DIRECTORIES:
            """
            We copy everything inside the directory to the destination.
            """
            for content in source.glob("*"):
                safe_move(console, content, destination)
        else:
            safe_move(console, source, destination)
