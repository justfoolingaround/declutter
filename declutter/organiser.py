from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Union

import regex

from .content_mime import NOT_CATEGORIZED, mimes


def pluralise(content_name: str):
    _ = content_name.capitalize()

    if _.endswith("s") or _.endswith("x"):
        return _ + "es"

    return _ + "s"


def list_content(dictionary: defaultdict):
    """
    Get all content within the lists of the dictionary.
    """
    for _, __ in dictionary.items():
        if isinstance(__, dict):
            yield from list_content(__)

        if isinstance(__, (list, tuple, set)):
            yield from __


def get_content_type(
    content_extension: str, *, content_types: dict[str, Union[str, dict]] = mimes
) -> Tuple[str]:
    for type_of, types in content_types.items():
        if type_of == NOT_CATEGORIZED:
            return ()

        if isinstance(types, dict):
            if any(
                regex.match(pattern + "$", content_extension, flags=regex.I)
                for pattern in list_content(types)
            ):
                return (
                    type_of,
                    *get_content_type(content_extension, content_types=types),
                )
            continue

        for pattern in types:
            if regex.match(pattern + "$", content_extension, flags=regex.I):
                return (type_of,)

    return ()


def get_directory_type(path: Path) -> Dict[Tuple[str], List[Path]]:
    """
    Get the possible types of the content in the directory recursively.
    """
    beacon = defaultdict(list)

    for content in path.glob("*"):
        if content.is_dir():
            if content.name in (".github", ".git"):
                beacon.clear()
                beacon.update({("developer",): [content.parent]})
                return beacon

            beacon.update(get_directory_type(content))

        if not "." in content.name:
            beacon[()].append(content)
            continue

        _, extension = content.name.rsplit(".", 1)
        beacon[get_content_type(extension)].append(content)

    return beacon


def get_absolute_directory_type(path: Path):

    directory_beacon = get_directory_type(path)

    for type_of, paths in directory_beacon.items():
        total_path_size = sum(map(lambda path: path.stat().st_size, paths))
        yield type_of, total_path_size


def get_transfer_route(current_path: Path, directory_tuple: Tuple[str]):
    if not directory_tuple:
        return current_path

    raw_copy = current_path

    for directory in directory_tuple:
        raw_copy /= pluralise(directory)
        raw_copy.mkdir(exist_ok=True)

    return raw_copy


def iter_organisation(path: Path):
    for content in path.glob("*"):
        if content.is_dir():
            directory_types = sorted(
                get_absolute_directory_type(content), key=lambda x: x[1], reverse=True
            )
            if not directory_types:
                continue
            type_of, *_ = directory_types[0]
            yield content, get_transfer_route(path, type_of)
            continue

        if not "." in content.name:
            yield content, path
            continue

        _, extension = content.name.rsplit(".", 1)

        yield content, get_transfer_route(path, get_content_type(extension))
