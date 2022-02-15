"""
See what exactly is allocating the working directory.
"""


from pathlib import Path

import click
import rich
from rich.table import Table
from rich.live import Live

from ... import get_absolute_directory_type

def sizeof_fmt(num, suffix="B", divisor=1024.0):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < divisor:
            return "{:3.1f}{}{}".format(num, unit, suffix)
        num /= divisor
    return "{:3.1f}Yi{}".format(num, suffix)

@click.command()
@click.argument("path", required=False, default=".", type=str)
def declutter_what_command(path):

    table = Table(
        title="declutter - File category allocation", title_style="bold magenta"
    )

    table.add_column("Content Type", justify="left")
    table.add_column("Bytes Allocated", justify="left")

    with Live(table):

        sizes = []

        for type_of, path_size in get_absolute_directory_type(Path(path)):
            table.add_row(
                "/".join(map(str.capitalize, type_of)) or "Other",
                "{} ({} bytes)".format(sizeof_fmt(path_size), path_size),
            )
            sizes.append(path_size)

        table.add_column("Percentage allocated", justify="left")
        table.columns[-1]._cells.extend(
            "{0:.2f}%".format(size / sum(sizes) * 100) for size in sizes
        )
