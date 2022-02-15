"""
Organise directories 
"""

from pathlib import Path
from shutil import move

import click
import rich

from ... import iter_organisation


@click.command()
@click.argument("path", required=False, default=".", type=str)
@click.option(
    "-e",
    "--exempt",
    help="Path that are not to be touched during the procedure.",
    required=False,
    multiple=True,
)
def declutter_organise_command(path, exempt):
    exempt_path = map(Path, exempt)
    console = rich.get_console()

    for source, destination in (
        (src, dest)
        for src, dest in iter_organisation(Path(path))
        if not (
            dest in (src, src.parent)
            or src == dest.parent
            or any(check == src for check in exempt_path)
        )
    ):
        try:
            move(source, destination)
        except Exception as e:
            console.print(
                "[red]Could not move {} to {} due to {!r}.[/red]".format(
                    source, destination, e
                )
            )
