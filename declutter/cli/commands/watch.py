"""
Track changes to files and directories.
"""


import asyncio
import time
from datetime import datetime
from pathlib import Path

import click
import rich


async def watch_file(console, path: Path, *, delay=1.0):
    """
    Watch a file for changes and run a command when they occur.
    """
    mtime = time.time()

    while 1:
        if path.stat().st_mtime > mtime:
            dt_now = datetime.now()
            console.print(
                "{} 👀 | [green]{}[/green]".format(
                    dt_now.strftime("%Y-%m-%d %H:%M:%S"), path
                )
            )
            mtime = path.stat().st_mtime

        await asyncio.sleep(delay)


@click.command()
@click.argument("path", required=False, default=".", type=str)
@click.argument("delay", required=False, default=1.0, type=float)
def declutter_watch_command(path: str, delay: float):
    console = rich.get_console()

    resolved_path = Path(path).resolve(strict=True)

    if resolved_path.is_dir():
        gather_files = (_ for _ in resolved_path.glob("**/*") if _.is_file())
    else:
        gather_files = [resolved_path]

    if not gather_files:
        return console.print("[red]No files to watch.[/red]")

    task = asyncio.gather(*(watch_file(console, _, delay=delay) for _ in gather_files))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
