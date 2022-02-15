"""
Makes a list of old directories within a massive directory for archiving.
"""

import time
from datetime import datetime
from pathlib import Path

import click
import rich
from rich.table import Table
from rich.live import Live


def get_old_directories(path: Path):
    """
    Get a list of old directories within a massive directory.
    """
    mtime = time.time()

    for content in path.iterdir():
        if content.is_dir():
            modified_time = content.stat().st_mtime
            if mtime - modified_time > 2592000:
                yield content, modified_time


@click.command()
@click.argument("path", required=False, default=".", type=str)
def declutter_oldies_command(path):
    console = rich.get_console()

    resolved_path = Path(path).resolve(strict=True)

    if not resolved_path.is_dir():
        return console.print("[red]{} is not a directory.[/red]".format(resolved_path))

    table = Table(
        title="declutter - Old Directories and files", title_style="bold magenta"
    )

    table.add_column("Path", justify="left")
    table.add_column("Date Modified", justify="left")

    with Live(table):
        for content, modified_time in sorted(
            get_old_directories(resolved_path), key=lambda x: x[1], reverse=True
        ):
            table.add_row(
                content.as_posix(),
                datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S"),
            )

        table.caption = (
            "Archiving old directories and files can save you a lot of memory!"
        )
